import os
import re
import subprocess
import sys
from tkinter import filedialog, messagebox

import customtkinter as ctk

from app.pages.base_page import BasePage
from app.services.config_manager import ConfigManager
from app.services.ledger_generator import (
    create_general_ledger,
    generate_trial_balance,
    generate_yearly_trial_balance,
)


LEDGER_DIR = "./output/総勘定元帳and試算表"


class LedgerPage(BasePage):
    def __init__(self, parent, config=None):
        super().__init__(parent)

        self.config = config or ConfigManager()
        self._step1_folder = None
        self._step2_folder = None
        self._step3_folder = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        outer = ctk.CTkFrame(self, fg_color="transparent")
        outer.grid(row=0, column=0, sticky="nsew")
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(outer, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.95)
        container.grid_columnconfigure((0, 1, 2), weight=1)
        container.grid_rowconfigure((1, 2, 3), weight=1)

        # Page title (row 0, spans 3 columns)
        title_row = ctk.CTkFrame(container, fg_color="transparent")
        title_row.grid(row=0, column=0, columnspan=3, sticky="ew", padx=10, pady=(10, 10))
        title_row.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            title_row,
            text="帳簿生成",
            font=ctk.CTkFont(size=20, weight="bold"),
            anchor="w",
        )
        title.grid(row=0, column=0, sticky="w")

        # 一括実行 button
        self.batch_btn = ctk.CTkButton(
            title_row, text="⚡ 一括実行（全STEP）",
            font=ctk.CTkFont(size=13, weight="bold"), width=200, height=36,
            corner_radius=10, fg_color="#16a34a", hover_color="#15803d",
            border_width=1, border_color="#4ade80",
            command=self._run_all,
        )
        self.batch_btn.grid(row=0, column=1, sticky="e", padx=(10, 0))

        # ── 3x3 grid (rows 1-3, cols 0-2) ──

        # (row 1, col 0) STEP 1: 総勘定元帳
        step1 = self._create_card(container, "STEP 1", "総勘定元帳の作成")
        step1.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        self._build_step1(step1)

        # (row 1, col 1) STEP 2: 月度試算表
        step2 = self._create_card(container, "STEP 2", "月度試算表の作成")
        step2.grid(row=1, column=1, sticky="nsew", padx=6, pady=6)
        self._build_step2(step2)

        # (row 1, col 2) STEP 3: 年度試算表
        step3 = self._create_card(container, "STEP 3", "年度試算表の作成")
        step3.grid(row=1, column=2, sticky="nsew", padx=6, pady=6)
        self._build_step3(step3)

        # (row 2, col 0) empty
        self._create_empty_card(container).grid(row=2, column=0, sticky="nsew", padx=6, pady=6)

        # (row 2, col 1) 一括実行 status
        batch_card = self._create_card(container, "一括実行", "処理状況")
        batch_card.grid(row=2, column=1, sticky="nsew", padx=6, pady=6)
        batch_inner = ctk.CTkFrame(batch_card, fg_color="transparent")
        batch_inner.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        self.batch_status = ctk.CTkLabel(
            batch_inner, text="", font=ctk.CTkFont(size=10),
            text_color="#7f849c", anchor="nw", wraplength=220, justify="left",
        )
        self.batch_status.pack(fill="both", expand=True)

        # (row 2, col 2) empty
        self._create_empty_card(container).grid(row=2, column=2, sticky="nsew", padx=6, pady=6)

        # (row 3, col 0) empty
        self._create_empty_card(container).grid(row=3, column=0, sticky="nsew", padx=6, pady=6)

        # (row 3, col 1) empty
        self._create_empty_card(container).grid(row=3, column=1, sticky="nsew", padx=6, pady=6)

        # (row 3, col 2) empty
        self._create_empty_card(container).grid(row=3, column=2, sticky="nsew", padx=6, pady=6)

        # (row 4) Open folder
        self.open_btn = ctk.CTkButton(
            container, text="📂 出力フォルダを開く",
            font=ctk.CTkFont(size=13), height=36, corner_radius=10,
            fg_color="#64748b", hover_color="#475569",
            border_width=1, border_color="#94a3b8",
            command=self._open_folder,
        )
        self.open_btn.grid(row=4, column=0, columnspan=3, sticky="ew", padx=6, pady=(10, 6))

    def _build_step1(self, card):
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        inner.grid_columnconfigure(0, weight=1)

        self.step1_select_btn = ctk.CTkButton(
            inner, text="📁 仕訳帳フォルダを選択",
            font=ctk.CTkFont(size=12, weight="bold"), height=34,
            corner_radius=10, fg_color="#3b82f6", hover_color="#2563eb",
            border_width=1, border_color="#60a5fa",
            command=self._select_step1_folder,
        )
        self.step1_select_btn.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        self.step1_path_label = ctk.CTkLabel(
            inner, text="未選択", font=ctk.CTkFont(size=10),
            text_color="#6c7086", anchor="w",
        )
        self.step1_path_label.grid(row=1, column=0, sticky="w", pady=(0, 6))

        self.step1_btn = ctk.CTkButton(
            inner, text="⚡ 生成",
            font=ctk.CTkFont(size=12, weight="bold"), height=34, corner_radius=10,
            fg_color="#8b5cf6", hover_color="#7c3aed",
            border_width=1, border_color="#a78bfa",
            command=self._run_step1,
        )
        self.step1_btn.grid(row=2, column=0, sticky="ew", pady=(2, 4))

        self.step1_status = ctk.CTkLabel(
            inner, text="", font=ctk.CTkFont(size=10),
            text_color="#7f849c", anchor="nw", wraplength=200, justify="left",
        )
        self.step1_status.grid(row=3, column=0, sticky="nw")

    def _build_step2(self, card):
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        inner.grid_columnconfigure(0, weight=1)

        self.step2_select_btn = ctk.CTkButton(
            inner, text="📁 元帳フォルダを選択",
            font=ctk.CTkFont(size=12, weight="bold"), height=34,
            corner_radius=10, fg_color="#3b82f6", hover_color="#2563eb",
            border_width=1, border_color="#60a5fa",
            command=self._select_step2_folder,
        )
        self.step2_select_btn.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        self.step2_path_label = ctk.CTkLabel(
            inner, text="未選択", font=ctk.CTkFont(size=10),
            text_color="#6c7086", anchor="w",
        )
        self.step2_path_label.grid(row=1, column=0, sticky="w", pady=(0, 6))

        # Month dropdown
        month_row = ctk.CTkFrame(inner, fg_color="transparent")
        month_row.grid(row=2, column=0, sticky="ew", pady=(0, 4))
        month_row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(month_row, text="対象月:", font=ctk.CTkFont(size=11), anchor="w").grid(
            row=0, column=0, padx=(0, 6)
        )
        year = self.config.year
        month_values = ["全月"] + [f"{year}{m:02d}" for m in range(1, 13)]
        self.step2_combo = ctk.CTkComboBox(
            month_row, values=month_values, font=ctk.CTkFont(size=12), height=30, state="readonly"
        )
        self.step2_combo.grid(row=0, column=1, sticky="ew")
        self.step2_combo.set("全月")

        self.step2_btn = ctk.CTkButton(
            inner, text="⚡ 生成",
            font=ctk.CTkFont(size=12, weight="bold"), height=34, corner_radius=10,
            fg_color="#8b5cf6", hover_color="#7c3aed",
            border_width=1, border_color="#a78bfa",
            command=self._run_step2,
        )
        self.step2_btn.grid(row=3, column=0, sticky="ew", pady=(2, 4))

        self.step2_status = ctk.CTkLabel(
            inner, text="", font=ctk.CTkFont(size=10),
            text_color="#7f849c", anchor="nw", wraplength=200, justify="left",
        )
        self.step2_status.grid(row=4, column=0, sticky="nw")

    def _build_step3(self, card):
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=12, pady=(0, 10))
        inner.grid_columnconfigure(0, weight=1)

        self.step3_select_btn = ctk.CTkButton(
            inner, text="📁 試算表フォルダを選択",
            font=ctk.CTkFont(size=12, weight="bold"), height=34,
            corner_radius=10, fg_color="#3b82f6", hover_color="#2563eb",
            border_width=1, border_color="#60a5fa",
            command=self._select_step3_folder,
        )
        self.step3_select_btn.grid(row=0, column=0, sticky="ew", pady=(0, 4))

        self.step3_path_label = ctk.CTkLabel(
            inner, text="未選択", font=ctk.CTkFont(size=10),
            text_color="#6c7086", anchor="w",
        )
        self.step3_path_label.grid(row=1, column=0, sticky="w", pady=(0, 6))

        year_text = f"対象年度：{self.config.year}年"
        ctk.CTkLabel(
            inner, text=year_text, font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#bac2de", anchor="w",
        ).grid(row=2, column=0, sticky="w", pady=(0, 4))

        self.step3_btn = ctk.CTkButton(
            inner, text="⚡ 生成",
            font=ctk.CTkFont(size=12, weight="bold"), height=34, corner_radius=10,
            fg_color="#8b5cf6", hover_color="#7c3aed",
            border_width=1, border_color="#a78bfa",
            command=self._run_step3,
        )
        self.step3_btn.grid(row=3, column=0, sticky="ew", pady=(2, 4))

        self.step3_status = ctk.CTkLabel(
            inner, text="", font=ctk.CTkFont(size=10),
            text_color="#7f849c", anchor="nw", wraplength=200, justify="left",
        )
        self.step3_status.grid(row=4, column=0, sticky="nw")

    # ── Helper: create step card ──
    def _create_card(self, parent, step_label, title):
        card = ctk.CTkFrame(parent, border_width=1, border_color="#313244", corner_radius=10, fg_color="#1e1e2e")

        header = ctk.CTkFrame(card, fg_color="transparent")
        header.pack(fill="x", padx=12, pady=(10, 6))

        ctk.CTkLabel(
            header, text=step_label,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#8b5cf6",
        ).pack(anchor="w")

        ctk.CTkLabel(
            header, text=title,
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#cdd6f4",
        ).pack(anchor="w")

        return card

    def _create_empty_card(self, parent):
        return ctk.CTkFrame(
            parent, border_width=1, border_color="#252536",
            corner_radius=10, fg_color="#181825",
        )

    # ── on_show ──
    def on_show(self):
        pass

    # ── Step 1: select folder with 仕訳帳 CSVs ──
    def _select_step1_folder(self):
        folder = filedialog.askdirectory(title="仕訳帳CSVが含まれるフォルダを選択")
        if not folder:
            return
        self._step1_folder = folder
        self.step1_path_label.configure(text=os.path.basename(folder) or folder, text_color="#a6adc8")

    def _find_journal_csvs(self, folder):
        """Find all 仕訳帳_YYYYMM.csv files in folder."""
        csvs = []
        if not folder or not os.path.isdir(folder):
            return csvs
        for f in sorted(os.listdir(folder)):
            if re.match(r"仕訳帳_\d{6}\.csv$", f):
                csvs.append(os.path.join(folder, f))
        return csvs

    def _run_step1(self):
        folder = self._step1_folder
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("エラー", "仕訳帳CSVが含まれるフォルダを選択してください。")
            return

        csv_files = self._find_journal_csvs(folder)
        if not csv_files:
            messagebox.showerror("エラー", "選択フォルダに仕訳帳CSVファイルが見つかりません。")
            return

        try:
            self.step1_status.configure(text="処理中...", text_color="#f59e0b")
            self.update_idletasks()

            all_messages = []
            for csv_path in csv_files:
                _files, _date, messages = create_general_ledger(csv_path, LEDGER_DIR)
                all_messages.extend(messages)

            status = "\n".join(all_messages)
            self.step1_status.configure(text=status, text_color="#16a34a")
        except Exception as e:
            self.step1_status.configure(text=f"エラー: {e}", text_color="#dc2626")
            messagebox.showerror("エラー", str(e))

    # ── Step 2: select folder with ledger files ──
    def _select_step2_folder(self):
        folder = filedialog.askdirectory(title="総勘定元帳フォルダを選択")
        if not folder:
            return
        self._step2_folder = folder
        self.step2_path_label.configure(text=os.path.basename(folder) or folder, text_color="#a6adc8")

    def _run_step2(self, target_folder=None):
        selected_month = self.step2_combo.get()
        folder = target_folder or self._step2_folder

        if not folder or not os.path.isdir(folder):
            messagebox.showerror("エラー", "元帳フォルダを選択してください。")
            return

        year = self.config.year

        if selected_month == "全月":
            # Find all unique months from ledger files
            months = set()
            for f in os.listdir(folder):
                m = re.match(r".+_(\d{6})\.csv$", f)
                if m and not f.startswith("試算表") and m.group(1).startswith(year):
                    months.add(m.group(1))
            months = sorted(months)
        else:
            months = [selected_month]

        if not months:
            messagebox.showerror("エラー", f"{year}年の総勘定元帳が見つかりません。")
            return

        try:
            self.step2_status.configure(text="処理中...", text_color="#f59e0b")
            self.update_idletasks()

            created = []
            for month in months:
                ledger_files = []
                for f in os.listdir(folder):
                    if f.endswith(f"_{month}.csv") and not f.startswith("試算表"):
                        ledger_files.append(os.path.join(folder, f))

                if ledger_files:
                    tb_path = generate_trial_balance(ledger_files, month, folder)
                    created.append(os.path.basename(tb_path))

            status = "\n".join(f"作成: {name}" for name in created)
            self.step2_status.configure(text=status or "対象なし", text_color="#16a34a")
        except Exception as e:
            self.step2_status.configure(text=f"エラー: {e}", text_color="#dc2626")
            messagebox.showerror("エラー", str(e))

    # ── Step 3: select folder with monthly trial balances ──
    def _select_step3_folder(self):
        folder = filedialog.askdirectory(title="月度試算表フォルダを選択")
        if not folder:
            return
        self._step3_folder = folder
        self.step3_path_label.configure(text=os.path.basename(folder) or folder, text_color="#a6adc8")

    def _run_step3(self, target_folder=None):
        year = self.config.year
        folder = target_folder or self._step3_folder
        if not folder or not os.path.isdir(folder):
            messagebox.showerror("エラー", "試算表フォルダを選択してください。")
            return

        tb_files = []
        for f in os.listdir(folder):
            match = re.match(r"試算表_(\d{6})\.csv$", f)
            if match and match.group(1).startswith(year):
                tb_files.append(os.path.join(folder, f))

        if not tb_files:
            messagebox.showerror("エラー", f"{year}年の月度試算表が見つかりません。")
            return

        try:
            self.step3_status.configure(text="処理中...", text_color="#f59e0b")
            self.update_idletasks()

            tb_files.sort()
            out_path = generate_yearly_trial_balance(tb_files, year, folder)
            self.step3_status.configure(
                text=f"作成: {os.path.basename(out_path)}", text_color="#16a34a"
            )
        except Exception as e:
            self.step3_status.configure(text=f"エラー: {e}", text_color="#dc2626")
            messagebox.showerror("エラー", str(e))

    # ── Run all steps ──
    def _run_all(self):
        """Execute all 3 steps sequentially using default output folder."""
        # Ask user to select the folder containing 仕訳帳 CSVs
        folder = filedialog.askdirectory(title="仕訳帳CSVが含まれるフォルダを選択")
        if not folder:
            return

        csv_files = self._find_journal_csvs(folder)
        if not csv_files:
            messagebox.showerror("エラー", "選択フォルダに仕訳帳CSVファイルが見つかりません。")
            return

        try:
            self.batch_status.configure(text="STEP 1: 総勘定元帳を生成中...", text_color="#f59e0b")
            self.update_idletasks()

            # STEP 1: Generate general ledgers from all journal CSVs
            for csv_path in csv_files:
                create_general_ledger(csv_path, LEDGER_DIR)

            self.step1_status.configure(text="完了", text_color="#16a34a")
            self.batch_status.configure(text="STEP 1: 完了\nSTEP 2: 月度試算表を生成中...", text_color="#f59e0b")
            self.update_idletasks()

            # STEP 2: Generate monthly trial balances from ledger dir
            year = self.config.year
            months = set()
            for f in os.listdir(LEDGER_DIR):
                m = re.match(r".+_(\d{6})\.csv$", f)
                if m and not f.startswith("試算表") and m.group(1).startswith(year):
                    months.add(m.group(1))

            for month in sorted(months):
                ledger_files = []
                for f in os.listdir(LEDGER_DIR):
                    if f.endswith(f"_{month}.csv") and not f.startswith("試算表"):
                        ledger_files.append(os.path.join(LEDGER_DIR, f))
                if ledger_files:
                    generate_trial_balance(ledger_files, month, LEDGER_DIR)

            self.step2_status.configure(text="完了", text_color="#16a34a")
            self.batch_status.configure(
                text="STEP 1: 完了\nSTEP 2: 完了\nSTEP 3: 年度試算表を生成中...", text_color="#f59e0b"
            )
            self.update_idletasks()

            # STEP 3: Generate yearly trial balance
            tb_files = []
            for f in os.listdir(LEDGER_DIR):
                match = re.match(r"試算表_(\d{6})\.csv$", f)
                if match and match.group(1).startswith(year):
                    tb_files.append(os.path.join(LEDGER_DIR, f))

            if tb_files:
                tb_files.sort()
                generate_yearly_trial_balance(tb_files, year, LEDGER_DIR)

            self.step3_status.configure(text="完了", text_color="#16a34a")
            self.batch_status.configure(
                text="STEP 1: 完了\nSTEP 2: 完了\nSTEP 3: 完了\n\n全処理が完了しました！",
                text_color="#16a34a",
            )
        except Exception as e:
            self.batch_status.configure(text=f"エラー: {e}", text_color="#dc2626")
            messagebox.showerror("エラー", str(e))

    # ── Open folder ──
    def _open_folder(self):
        target = os.path.abspath(LEDGER_DIR)
        os.makedirs(target, exist_ok=True)
        if sys.platform == "win32":
            os.startfile(target)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", target])
        else:
            subprocess.Popen(["xdg-open", target])
