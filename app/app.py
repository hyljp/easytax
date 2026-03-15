from datetime import datetime

import customtkinter as ctk

from app.sidebar import Sidebar
from app.pages.invoice_page import InvoicePage
from app.pages.ledger_page import LedgerPage
from app.pages.financial_page import FinancialPage
from app.services.config_manager import ConfigManager


class YearSelectDialog(ctk.CTkToplevel):
    """Modal dialog with a year dropdown."""

    def __init__(self, parent, current_year):
        super().__init__(parent)
        self.title("会計年度の変更")
        self.geometry("300x150")
        self.resizable(False, False)
        self.grab_set()

        self._result = None

        now_year = datetime.now().year
        year_values = [str(y) for y in range(now_year - 3, now_year + 4)]

        ctk.CTkLabel(
            self, text="会計年度を選択してください",
            font=ctk.CTkFont(size=14),
        ).pack(pady=(20, 10))

        self.combo = ctk.CTkComboBox(
            self, values=year_values,
            font=ctk.CTkFont(size=14), width=120, height=32, state="readonly",
        )
        self.combo.set(current_year)
        self.combo.pack(pady=(0, 15))

        self.ok_btn = ctk.CTkButton(
            self, text="OK", width=80, height=32,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._on_ok,
        )
        self.ok_btn.pack()

        self.protocol("WM_DELETE_WINDOW", self._on_cancel)

    def _on_ok(self):
        self._result = self.combo.get()
        self.grab_release()
        self.destroy()

    def _on_cancel(self):
        self._result = None
        self.grab_release()
        self.destroy()

    def get_result(self):
        self.wait_window()
        return self._result


class EasyTaxApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("easyTax")
        self.geometry("1200x800")
        self.minsize(900, 600)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.config_manager = ConfigManager()

        # Layout: top bar (row 0, fixed) + main area (row 1, expand)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        # Top year label (spans full width)
        year_bar = ctk.CTkFrame(self, height=36, fg_color="#1e1e2e", corner_radius=0)
        year_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        year_bar.grid_columnconfigure(0, weight=1)
        year_bar.grid_propagate(False)

        self.year_label = ctk.CTkLabel(
            year_bar,
            text=f"会計年度：{self.config_manager.year}年",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#a0aec0",
            cursor="hand2",
        )
        self.year_label.pack(side="right", padx=20, pady=5)
        self.year_label.bind("<Button-1>", lambda e: self._change_year())

        # Sidebar
        self.sidebar = Sidebar(self, on_navigate=self.show_page)
        self.sidebar.grid(row=1, column=0, sticky="nsew")

        # Content container
        self.content = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.content.grid(row=1, column=1, sticky="nsew")
        self.content.grid_rowconfigure(0, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        # Pages
        self.pages = {}
        self.pages["invoice"] = InvoicePage(self.content)
        self.pages["page2"] = LedgerPage(self.content)
        self.pages["page3"] = FinancialPage(self.content)

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        # Show default page
        self.show_page("invoice")

    def _change_year(self):
        dialog = YearSelectDialog(self, self.config_manager.year)
        new_year = dialog.get_result()

        if not new_year or new_year == self.config_manager.year:
            return

        self.config_manager.data["THIS_YEAR"] = new_year
        self.config_manager.save()
        self.year_label.configure(text=f"会計年度：{new_year}年")

        # Rebuild pages to pick up new year
        for page in self.pages.values():
            page.grid_forget()
            page.destroy()

        self.pages = {}
        self.pages["invoice"] = InvoicePage(self.content)
        self.pages["page2"] = LedgerPage(self.content)
        self.pages["page3"] = FinancialPage(self.content)

        for page in self.pages.values():
            page.grid(row=0, column=0, sticky="nsew")

        self.show_page("invoice")

    def show_page(self, page_key):
        if page_key in self.pages:
            page = self.pages[page_key]
            page.tkraise()
            page.on_show()
            self.sidebar.set_active(page_key)
