import os
import subprocess
import sys
from tkinter import filedialog, messagebox

import customtkinter as ctk

from app.pages.base_page import BasePage
from app.services.config_manager import ConfigManager
from app.services.financial_statement_generator import (
    generate_balance_sheet,
    generate_income_statement,
)

OUTPUT_DIR = "./output/財務諸表"


class FinancialPage(BasePage):
    def __init__(self, parent, config=None):
        super().__init__(parent)

        self.config = config or ConfigManager()
        self._tb_csv_path = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Scrollable container
        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.grid(row=0, column=0, sticky="nsew")
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(outer, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.65, relheight=0.95)
        container.grid_columnconfigure(0, weight=1)

        row = 0

        # Page title
        title_row = ctk.CTkFrame(container, fg_color="transparent")
        title_row.grid(row=row, column=0, sticky="ew", padx=10, pady=(10, 15))
        title_row.grid_columnconfigure(0, weight=1)
        row += 1

        title = ctk.CTkLabel(
            title_row,
            text="財務諸表（青色申告）",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="w")

        # ── Trial balance CSV selection ──
        tb_card = self._create_card(container, "入力", "試算表の選択")
        tb_card.grid(row=row, column=0, sticky="ew", padx=10, pady=0)
        row += 1

        tb_inner = ctk.CTkFrame(tb_card, fg_color="transparent")
        tb_inner.pack(fill="x", padx=15, pady=(0, 12))
        tb_inner.grid_columnconfigure(1, weight=1)

        self.tb_select_btn = ctk.CTkButton(
            tb_inner, text="📁 試算表CSVを選択",
            font=ctk.CTkFont(size=13, weight="bold"), width=190, height=36,
            corner_radius=10, fg_color="#3b82f6", hover_color="#2563eb",
            border_width=1, border_color="#60a5fa",
            command=self._select_tb_csv,
        )
        self.tb_select_btn.grid(row=0, column=0, padx=(0, 10))

        self.tb_path_label = ctk.CTkLabel(
            tb_inner, text="", font=ctk.CTkFont(size=12),
            text_color="#a6adc8", anchor="w",
        )
        self.tb_path_label.grid(row=0, column=1, sticky="w")

        # 参照フォルダ button
        self.tb_folder_btn = ctk.CTkButton(
            tb_inner, text="📁 フォルダから自動選択",
            font=ctk.CTkFont(size=12), width=170, height=36,
            corner_radius=10, fg_color="#64748b", hover_color="#475569",
            border_width=1, border_color="#94a3b8",
            command=self._select_tb_from_folder,
        )
        self.tb_folder_btn.grid(row=1, column=0, columnspan=2, sticky="w", pady=(6, 0))

        # Arrow
        self._create_arrow(container).grid(row=row, column=0, pady=4)
        row += 1

        # ── Batch generate button ──
        self.batch_btn = ctk.CTkButton(
            container, text="⚡ 一括生成（損益計算書 + 貸借対照表）",
            font=ctk.CTkFont(size=14, weight="bold"), height=42, corner_radius=10,
            fg_color="#16a34a", hover_color="#15803d",
            border_width=1, border_color="#4ade80",
            command=self._run_all,
        )
        self.batch_btn.grid(row=row, column=0, sticky="ew", padx=10, pady=(0, 4))
        row += 1

        self.batch_status = ctk.CTkLabel(
            container, text="", font=ctk.CTkFont(size=11),
            text_color="#7f849c", anchor="w", wraplength=500, justify="left",
        )
        self.batch_status.grid(row=row, column=0, sticky="w", padx=15)
        row += 1

        # Arrow
        self._create_arrow(container).grid(row=row, column=0, pady=4)
        row += 1

        # ── Income Statement card ──
        pl_card = self._create_card(container, "STEP 1", "損益計算書の作成")
        pl_card.grid(row=row, column=0, sticky="ew", padx=10, pady=0)
        row += 1

        pl_inner = ctk.CTkFrame(pl_card, fg_color="transparent")
        pl_inner.pack(fill="x", padx=15, pady=(0, 12))
        pl_inner.grid_columnconfigure(0, weight=1)

        self.pl_btn = ctk.CTkButton(
            pl_inner, text="⚡ 損益計算書を生成",
            font=ctk.CTkFont(size=13, weight="bold"), height=36, corner_radius=10,
            fg_color="#8b5cf6", hover_color="#7c3aed",
            border_width=1, border_color="#a78bfa",
            command=self._run_income_statement,
        )
        self.pl_btn.grid(row=0, column=0, sticky="ew", pady=(4, 6))

        self.pl_status = ctk.CTkLabel(
            pl_inner, text="", font=ctk.CTkFont(size=11),
            text_color="#7f849c", anchor="w", wraplength=500, justify="left",
        )
        self.pl_status.grid(row=1, column=0, sticky="w")

        # Arrow
        self._create_arrow(container).grid(row=row, column=0, pady=4)
        row += 1

        # ── Balance Sheet card ──
        bs_card = self._create_card(container, "STEP 2", "貸借対照表の作成")
        bs_card.grid(row=row, column=0, sticky="ew", padx=10, pady=0)
        row += 1

        bs_inner = ctk.CTkFrame(bs_card, fg_color="transparent")
        bs_inner.pack(fill="x", padx=15, pady=(0, 12))
        bs_inner.grid_columnconfigure(0, weight=1)

        self.bs_btn = ctk.CTkButton(
            bs_inner, text="⚡ 貸借対照表を生成",
            font=ctk.CTkFont(size=13, weight="bold"), height=36, corner_radius=10,
            fg_color="#8b5cf6", hover_color="#7c3aed",
            border_width=1, border_color="#a78bfa",
            command=self._run_balance_sheet,
        )
        self.bs_btn.grid(row=0, column=0, sticky="ew", pady=(4, 6))

        self.bs_status = ctk.CTkLabel(
            bs_inner, text="", font=ctk.CTkFont(size=11),
            text_color="#7f849c", anchor="w", wraplength=500, justify="left",
        )
        self.bs_status.grid(row=1, column=0, sticky="w")

        # ── Open folder button ──
        self.open_btn = ctk.CTkButton(
            container, text="📂 出力フォルダを開く",
            font=ctk.CTkFont(size=13), height=36, corner_radius=10,
            fg_color="#64748b", hover_color="#475569",
            border_width=1, border_color="#94a3b8",
            command=self._open_folder,
        )
        self.open_btn.grid(row=row, column=0, sticky="ew", padx=10, pady=(15, 10))

    # ── Helper: create step card ──
    def _create_card(self, parent, step_label, title):
        card = ctk.CTkFrame(parent, border_width=1, border_color="#313244", corner_radius=10, fg_color="#1e1e2e")

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=15, pady=(12, 8))

        ctk.CTkLabel(
            header, text=step_label,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#8b5cf6",
        ).pack(side="left", padx=(0, 8))

        ctk.CTkLabel(
            header, text=title,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#cdd6f4",
        ).pack(side="left")

        return card

    def _create_arrow(self, parent):
        return ctk.CTkLabel(
            parent, text="↓", font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#585b70",
        )

    # ── on_show ──
    def on_show(self):
        pass

    # ── Select trial balance CSV ──
    def _select_tb_csv(self):
        path = filedialog.askopenfilename(
            title="試算表CSVファイルを選択",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not path:
            return
        self._tb_csv_path = path
        self.tb_path_label.configure(text=os.path.basename(path))

    def _select_tb_from_folder(self):
        """Select folder and auto-find the yearly trial balance CSV."""
        folder = filedialog.askdirectory(title="試算表が含まれるフォルダを選択")
        if not folder:
            return

        year = self.config.year
        # Look for yearly trial balance first
        yearly_name = f"試算表_{year}_年度.csv"
        yearly_path = os.path.join(folder, yearly_name)
        if os.path.exists(yearly_path):
            self._tb_csv_path = yearly_path
            self.tb_path_label.configure(text=yearly_name)
            return

        messagebox.showwarning(
            "注意",
            f"フォルダ内に年度試算表 ({yearly_name}) が見つかりません。\n"
            "先に帳簿生成ページで年度試算表を作成してください。",
        )

    # ── Generate Income Statement ──
    def _run_income_statement(self):
        if not self._tb_csv_path or not os.path.exists(self._tb_csv_path):
            messagebox.showerror("エラー", "試算表CSVファイルを選択してください。")
            return

        try:
            self.pl_status.configure(text="処理中...", text_color="#f59e0b")
            self.update_idletasks()

            config_data = self.config.data
            year = self.config.year
            out_path = generate_income_statement(self._tb_csv_path, config_data, year, OUTPUT_DIR)
            self.pl_status.configure(
                text=f"作成: {os.path.basename(out_path)}", text_color="#16a34a"
            )
        except Exception as e:
            self.pl_status.configure(text=f"エラー: {e}", text_color="#dc2626")
            messagebox.showerror("エラー", str(e))

    # ── Generate Balance Sheet ──
    def _run_balance_sheet(self):
        if not self._tb_csv_path or not os.path.exists(self._tb_csv_path):
            messagebox.showerror("エラー", "試算表CSVファイルを選択してください。")
            return

        try:
            self.bs_status.configure(text="処理中...", text_color="#f59e0b")
            self.update_idletasks()

            config_data = self.config.data
            year = self.config.year
            out_path = generate_balance_sheet(self._tb_csv_path, config_data, year, OUTPUT_DIR)
            self.bs_status.configure(
                text=f"作成: {os.path.basename(out_path)}", text_color="#16a34a"
            )
        except Exception as e:
            self.bs_status.configure(text=f"エラー: {e}", text_color="#dc2626")
            messagebox.showerror("エラー", str(e))

    # ── Run all: generate both at once ──
    def _run_all(self):
        if not self._tb_csv_path or not os.path.exists(self._tb_csv_path):
            messagebox.showerror("エラー", "試算表CSVファイルを選択してください。")
            return

        try:
            config_data = self.config.data
            year = self.config.year

            self.batch_status.configure(text="損益計算書を生成中...", text_color="#f59e0b")
            self.update_idletasks()

            pl_path = generate_income_statement(self._tb_csv_path, config_data, year, OUTPUT_DIR)
            self.pl_status.configure(text=f"作成: {os.path.basename(pl_path)}", text_color="#16a34a")

            self.batch_status.configure(text="貸借対照表を生成中...", text_color="#f59e0b")
            self.update_idletasks()

            bs_path = generate_balance_sheet(self._tb_csv_path, config_data, year, OUTPUT_DIR)
            self.bs_status.configure(text=f"作成: {os.path.basename(bs_path)}", text_color="#16a34a")

            self.batch_status.configure(
                text=f"完了: {os.path.basename(pl_path)}, {os.path.basename(bs_path)}",
                text_color="#16a34a",
            )
        except Exception as e:
            self.batch_status.configure(text=f"エラー: {e}", text_color="#dc2626")
            messagebox.showerror("エラー", str(e))

    # ── Open folder ──
    def _open_folder(self):
        target = OUTPUT_DIR if os.path.isdir(OUTPUT_DIR) else "./output"
        if os.path.isdir(target):
            if sys.platform == "win32":
                os.startfile(target)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", target])
            else:
                subprocess.Popen(["xdg-open", target])
