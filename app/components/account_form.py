import customtkinter as ctk


class AccountForm(ctk.CTkFrame):
    def __init__(self, parent, on_write=None, on_kind_changed=None):
        super().__init__(parent, fg_color="transparent")
        self._on_write = on_write
        self._on_kind_changed = on_kind_changed

        self.grid_columnconfigure(0, weight=1)

        row = 0

        # Section: Account category
        section_label = ctk.CTkLabel(
            self,
            text="勘定科目",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        )
        section_label.grid(row=row, column=0, sticky="w", padx=10, pady=(10, 5))
        row += 1

        kind_label = ctk.CTkLabel(self, text="種類", font=ctk.CTkFont(size=12), anchor="w")
        kind_label.grid(row=row, column=0, sticky="w", padx=15, pady=(2, 0))
        row += 1

        self.kind_combo = ctk.CTkComboBox(
            self,
            values=[],
            font=ctk.CTkFont(size=13),
            height=32,
            state="readonly",
            command=self._kind_changed,
        )
        self.kind_combo.grid(row=row, column=0, sticky="ew", padx=15, pady=(0, 5))
        self.kind_combo.set("")
        row += 1

        item_label = ctk.CTkLabel(self, text="項目", font=ctk.CTkFont(size=12), anchor="w")
        item_label.grid(row=row, column=0, sticky="w", padx=15, pady=(2, 0))
        row += 1

        self.item_combo = ctk.CTkComboBox(
            self,
            values=[],
            font=ctk.CTkFont(size=13),
            height=32,
            state="readonly",
        )
        self.item_combo.grid(row=row, column=0, sticky="ew", padx=15, pady=(0, 10))
        self.item_combo.set("")
        row += 1

        # Separator
        sep = ctk.CTkFrame(self, height=1, fg_color="#313244")
        sep.grid(row=row, column=0, sticky="ew", padx=10, pady=5)
        row += 1

        # Section: Receipt info
        receipt_label = ctk.CTkLabel(
            self,
            text="レシート情報",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w",
        )
        receipt_label.grid(row=row, column=0, sticky="w", padx=10, pady=(5, 5))
        row += 1

        price_label = ctk.CTkLabel(self, text="価額", font=ctk.CTkFont(size=12), anchor="w")
        price_label.grid(row=row, column=0, sticky="w", padx=15, pady=(2, 0))
        row += 1

        self.price_entry = ctk.CTkEntry(self, font=ctk.CTkFont(size=13), height=32, placeholder_text="例: 1000")
        self.price_entry.grid(row=row, column=0, sticky="ew", padx=15, pady=(0, 5))
        row += 1

        date_label = ctk.CTkLabel(self, text="日付（MMDD）", font=ctk.CTkFont(size=12), anchor="w")
        date_label.grid(row=row, column=0, sticky="w", padx=15, pady=(2, 0))
        row += 1

        self.date_entry = ctk.CTkEntry(self, font=ctk.CTkFont(size=13), height=32, placeholder_text="例: 0315")
        self.date_entry.grid(row=row, column=0, sticky="ew", padx=15, pady=(0, 5))
        row += 1

        payment_label = ctk.CTkLabel(self, text="支払方式", font=ctk.CTkFont(size=12), anchor="w")
        payment_label.grid(row=row, column=0, sticky="w", padx=15, pady=(2, 0))
        row += 1

        self.payment_combo = ctk.CTkComboBox(
            self,
            values=[],
            font=ctk.CTkFont(size=13),
            height=32,
            state="readonly",
        )
        self.payment_combo.grid(row=row, column=0, sticky="ew", padx=15, pady=(0, 5))
        self.payment_combo.set("")
        row += 1

        comment_label = ctk.CTkLabel(self, text="備考", font=ctk.CTkFont(size=12), anchor="w")
        comment_label.grid(row=row, column=0, sticky="w", padx=15, pady=(2, 0))
        row += 1

        self.comment_entry = ctk.CTkEntry(self, font=ctk.CTkFont(size=13), height=32, placeholder_text="概要を入力")
        self.comment_entry.grid(row=row, column=0, sticky="ew", padx=15, pady=(0, 5))
        row += 1

        invoice_label = ctk.CTkLabel(self, text="INVOICE番号", font=ctk.CTkFont(size=12), anchor="w")
        invoice_label.grid(row=row, column=0, sticky="w", padx=15, pady=(2, 0))
        row += 1

        self.invoice_entry = ctk.CTkEntry(self, font=ctk.CTkFont(size=13), height=32)
        self.invoice_entry.insert(0, "NA")
        self.invoice_entry.grid(row=row, column=0, sticky="ew", padx=15, pady=(0, 15))
        row += 1

        # Write button
        self.write_btn = ctk.CTkButton(
            self,
            text="✎  書き込み",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=44,
            corner_radius=12,
            fg_color="#16a34a",
            hover_color="#15803d",
            border_width=1,
            border_color="#22c55e",
            command=self._write_click,
        )
        self.write_btn.grid(row=row, column=0, sticky="ew", padx=15, pady=(5, 10))

    def set_kinds(self, kinds):
        self.kind_combo.configure(values=kinds)

    def set_items(self, items):
        self.item_combo.configure(values=items)
        self.item_combo.set("")

    def set_payment_methods(self, methods):
        self.payment_combo.configure(values=methods)
        if methods:
            self.payment_combo.set(methods[0])

    def get_data(self):
        return {
            "kind": self.kind_combo.get(),
            "item": self.item_combo.get(),
            "price": self.price_entry.get().strip(),
            "date": self.date_entry.get().strip(),
            "payment": self.payment_combo.get(),
            "comment": self.comment_entry.get().strip(),
            "invoice_number": self.invoice_entry.get().strip(),
        }

    def reset(self, default_kind="", default_item=""):
        self.price_entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.comment_entry.delete(0, "end")
        self.invoice_entry.delete(0, "end")
        self.invoice_entry.insert(0, "NA")
        self.kind_combo.set(default_kind)
        if self._on_kind_changed and default_kind:
            self._on_kind_changed(default_kind)
        self.item_combo.set(default_item)

    def _kind_changed(self, value):
        if self._on_kind_changed:
            self._on_kind_changed(value)

    def _write_click(self):
        if self._on_write:
            self._on_write()
