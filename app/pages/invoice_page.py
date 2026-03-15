import os
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image

from app.pages.base_page import BasePage
from app.components.image_viewer import ImageViewer
from app.components.account_form import AccountForm
from app.services.config_manager import ConfigManager
from app.services.image_navigator import ImageNavigator, move_file
from app.services.csv_manager import write_to_journal, DuplicateVoucherError, DuplicateEntryError


OUTPUT_DIR = "./output"
PHOTO_DIR = "./output/photo"


class InvoicePage(BasePage):
    def __init__(self, parent):
        super().__init__(parent)

        self.config = ConfigManager()
        self.navigator = ImageNavigator()
        self.current_image = None  # PIL Image of current (possibly rotated)
        self._zoom = 1.0

        # Layout: 2 columns
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        # Left: image viewer
        self.image_viewer = ImageViewer(
            self,
            on_folder_selected=self._choose_folder,
            on_prev=self._show_prev,
            on_next=self._show_next,
            on_rotate=self._rotate,
            on_zoom_in=self._zoom_in,
            on_zoom_out=self._zoom_out,
        )
        self.image_viewer.grid(row=0, column=0, sticky="nsew", padx=(5, 2), pady=5)

        # Right panel: form only
        right_panel = ctk.CTkFrame(self, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(2, 5), pady=5)
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)

        # Account form
        self.account_form = AccountForm(
            right_panel,
            on_write=self._write_data,
            on_kind_changed=self._on_kind_changed,
        )
        self.account_form.grid(row=0, column=0, sticky="new", padx=0, pady=0)
        self.account_form.set_kinds(self.config.account_kinds)
        self.account_form.set_payment_methods(self.config.payment_methods)

        # Set defaults: 費用 → 接待交際費
        self.account_form.kind_combo.set("費用")
        self._on_kind_changed("費用")
        self.account_form.item_combo.set("接待交際費")

        # Bind canvas resize to redraw
        self.image_viewer.canvas.bind("<Configure>", self._on_canvas_resize)

    def on_show(self):
        pass

    def _choose_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return

        self.navigator.set_folder(folder)
        if self.navigator.has_images:
            path = self.navigator.next_image()
            self._display_image(path)
        else:
            messagebox.showinfo("情報", "画像ファイルが見つかりません。")

    def _show_prev(self):
        if not self.navigator.has_images:
            messagebox.showinfo("情報", "画像フォルダを選択してください。")
            return
        path = self.navigator.previous_image()
        if path:
            self._display_image(path)

    def _show_next(self):
        if not self.navigator.has_images:
            messagebox.showinfo("情報", "画像フォルダを選択してください。")
            return
        path = self.navigator.next_image()
        if path:
            self._display_image(path)

    def _rotate(self):
        if self.current_image is None:
            messagebox.showinfo("情報", "回転する画像がありません。")
            return
        self.current_image = self.current_image.rotate(270, expand=True)
        self._redraw()

    def _zoom_in(self):
        if self.current_image is None:
            return
        self._zoom = min(self._zoom + 0.25, 5.0)
        self._update_zoom_label()
        self._redraw()

    def _zoom_out(self):
        if self.current_image is None:
            return
        self._zoom = max(self._zoom - 0.25, 0.25)
        self._update_zoom_label()
        self._redraw()

    def _update_zoom_label(self):
        self.image_viewer.set_zoom_text(f"{int(self._zoom * 100)}%")

    def _display_image(self, path):
        if self.current_image:
            self.current_image.close()
        with Image.open(path) as img:
            self.current_image = img.copy()
        self._zoom = 1.0
        self._update_zoom_label()
        self.navigator.draw_on_canvas(self.image_viewer.canvas, image_path=path, zoom=self._zoom)
        self.image_viewer.set_path_text(os.path.basename(path))
        self.image_viewer.set_counter_text(
            f"{self.navigator.current_position} / {self.navigator.count}"
        )

    def _redraw(self):
        if self.current_image:
            self.navigator.draw_on_canvas(self.image_viewer.canvas, image=self.current_image, zoom=self._zoom)

    def _on_canvas_resize(self, event=None):
        if self.navigator.current_image_path:
            self._redraw()

    def _on_kind_changed(self, kind):
        items = self.config.get_account_items(kind)
        self.account_form.set_items(items)

    def _write_data(self):
        if not self.navigator.current_image_path:
            messagebox.showerror("エラー", "処理する画像がありません。")
            return

        data = self.account_form.get_data()
        date_val = data["date"]
        price_val = data["price"]
        comment_val = data["comment"]
        account_item = data["item"]
        payment_method = data["payment"]
        invoice_number = data["invoice_number"]

        if not (date_val and price_val and account_item and payment_method):
            messagebox.showerror("エラー", "日付、価額、勘定項目、および支払方式は必須です。")
            return

        write_date = self.config.year + date_val
        write_year_month = write_date[:6]
        output_photo_dir = os.path.join(PHOTO_DIR, write_year_month)

        src_path = self.navigator.current_image_path
        renamed_base = f"{date_val}_{price_val}_{comment_val}"

        msg = (
            f"以下の内容で書き込みますか？\n\n"
            f"日付: {write_date}\n"
            f"価額: {price_val}\n"
            f"支払方式: {payment_method}\n"
            f"備考: {comment_val}\n"
            f"勘定項目: {account_item}\n"
            f"INVOICE番号: {invoice_number}"
        )
        if not messagebox.askyesno("確認", msg):
            return

        try:
            journal_data = {
                "date": write_date,
                "price": price_val,
                "account_item": account_item,
                "comment": comment_val,
                "payment_method": payment_method,
                "voucher_number": renamed_base,
                "invoice_number": invoice_number,
            }
            write_to_journal(
                journal_data,
                self.config.journal_headers,
                self.config.journal_fields,
                OUTPUT_DIR,
            )

            if self.current_image:
                self.current_image.close()
                self.current_image = None

            move_file(src_path, output_photo_dir, date_val, comment_val, price_val)

            self.navigator.remove_current()
            self.account_form.reset(default_kind="費用", default_item="接待交際費")

            if self.navigator.has_images:
                path = self.navigator.next_image()
                if path:
                    self._display_image(path)
                else:
                    self._clear_canvas()
            else:
                self._clear_canvas()
                messagebox.showinfo("完了", "すべての画像を処理しました。")

        except DuplicateVoucherError as e:
            messagebox.showwarning("重複", str(e))
        except DuplicateEntryError as e:
            messagebox.showwarning("重複", str(e))
        except Exception as e:
            messagebox.showerror("エラー", f"書き込み中にエラーが発生しました:\n{e}")

    def _clear_canvas(self):
        self.image_viewer.canvas.delete("all")
        self.image_viewer.set_path_text("")
        self.image_viewer.set_counter_text("")
        self.current_image = None

