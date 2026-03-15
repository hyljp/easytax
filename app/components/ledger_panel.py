import os
import subprocess
import sys
import customtkinter as ctk


class LedgerPanel(ctk.CTkFrame):
    def __init__(self, parent, on_generate=None, output_dir="./output"):
        super().__init__(parent, fg_color="transparent")
        self._on_generate = on_generate
        self._output_dir = output_dir

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        row = 0

        # Section header
        sep = ctk.CTkFrame(self, height=1, fg_color="#dddddd")
        sep.grid(row=row, column=0, sticky="ew", padx=10, pady=(10, 5))
        row += 1

        header = ctk.CTkLabel(
            self,
            text="帳簿生成",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        )
        header.grid(row=row, column=0, sticky="w", padx=10, pady=(5, 5))
        row += 1

        csv_label = ctk.CTkLabel(self, text="仕訳帳CSV", font=ctk.CTkFont(size=12), anchor="w")
        csv_label.grid(row=row, column=0, sticky="w", padx=15, pady=(2, 0))
        row += 1

        self.csv_combo = ctk.CTkComboBox(
            self,
            values=[],
            font=ctk.CTkFont(size=13),
            height=32,
            state="readonly",
        )
        self.csv_combo.grid(row=row, column=0, sticky="ew", padx=15, pady=(0, 5))
        self.csv_combo.set("")
        row += 1

        # Buttons row
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=row, column=0, sticky="ew", padx=15, pady=(0, 5))
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.refresh_btn = ctk.CTkButton(
            btn_frame,
            text="↻ 更新",
            font=ctk.CTkFont(size=12),
            width=80,
            height=34,
            corner_radius=10,
            fg_color="#64748b",
            hover_color="#475569",
            border_width=1,
            border_color="#94a3b8",
            command=self.refresh_csv_list,
        )
        self.refresh_btn.grid(row=0, column=0, padx=3)

        self.generate_btn = ctk.CTkButton(
            btn_frame,
            text="⚡ 生成",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=80,
            height=34,
            corner_radius=10,
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            border_width=1,
            border_color="#a78bfa",
            command=self._generate_click,
        )
        self.generate_btn.grid(row=0, column=1, padx=3)

        self.open_btn = ctk.CTkButton(
            btn_frame,
            text="📂 フォルダ",
            font=ctk.CTkFont(size=12),
            width=80,
            height=34,
            corner_radius=10,
            fg_color="#64748b",
            hover_color="#475569",
            border_width=1,
            border_color="#94a3b8",
            command=self._open_folder,
        )
        self.open_btn.grid(row=0, column=2, padx=3)
        row += 1

        # Status log
        self.log_box = ctk.CTkTextbox(
            self,
            font=ctk.CTkFont(size=11),
            height=100,
            state="disabled",
            fg_color="#f8f9fa",
            text_color="#333333",
            corner_radius=6,
        )
        self.log_box.grid(row=row, column=0, sticky="nsew", padx=15, pady=(0, 10))

    def set_output_dir(self, output_dir):
        self._output_dir = output_dir
        self.refresh_csv_list()

    def refresh_csv_list(self):
        csv_files = []
        if os.path.isdir(self._output_dir):
            for f in os.listdir(self._output_dir):
                if f.startswith("仕訳帳_") and f.endswith(".csv"):
                    csv_files.append(f)
        csv_files.sort(reverse=True)
        self.csv_combo.configure(values=csv_files)
        if csv_files:
            self.csv_combo.set(csv_files[0])
        else:
            self.csv_combo.set("")

    def get_selected_csv(self):
        selected = self.csv_combo.get()
        if selected:
            return os.path.join(self._output_dir, selected)
        return None

    def log(self, message):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", message + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def clear_log(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.configure(state="disabled")

    def _generate_click(self):
        if self._on_generate:
            self._on_generate()

    def _open_folder(self):
        target = self._output_dir
        if os.path.isdir(target):
            if sys.platform == "win32":
                os.startfile(target)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", target])
            else:
                subprocess.Popen(["xdg-open", target])
