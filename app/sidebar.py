import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    NAV_ITEMS = [
        ("invoice", "仕訳入力"),
        ("page2", "帳簿生成"),
        ("page3", "財務諸表"),
    ]

    COLOR_BG = "#11111b"
    COLOR_ACTIVE = "#1e1e3a"
    COLOR_HOVER = "#181825"
    COLOR_TEXT = "#cdd6f4"

    def __init__(self, parent, on_navigate=None):
        super().__init__(parent, width=200, fg_color=self.COLOR_BG, corner_radius=0)
        self.grid_propagate(False)
        self._on_navigate = on_navigate
        self._buttons = {}
        self._active_page = None

        # Title
        title = ctk.CTkLabel(
            self,
            text="easyTax",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=self.COLOR_TEXT,
        )
        title.pack(pady=(25, 5), padx=15, anchor="w")

        # Subtitle
        subtitle = ctk.CTkLabel(
            self,
            text="会計管理ソフト",
            font=ctk.CTkFont(size=11),
            text_color="#6c7086",
        )
        subtitle.pack(padx=15, anchor="w")

        # Separator
        sep = ctk.CTkFrame(self, height=1, fg_color="#313244")
        sep.pack(fill="x", padx=15, pady=(15, 10))

        # Nav buttons with icons
        nav_icons = {
            "invoice": "📋",
            "page2": "📊",
            "page3": "⚙️",
        }
        for key, label in self.NAV_ITEMS:
            icon = nav_icons.get(key, "")
            btn = ctk.CTkButton(
                self,
                text=f"  {icon}  {label}",
                anchor="w",
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                text_color=self.COLOR_TEXT,
                hover_color=self.COLOR_HOVER,
                height=42,
                corner_radius=10,
                border_width=0,
                command=lambda k=key: self._on_click(k),
            )
            btn.pack(fill="x", padx=10, pady=3)
            self._buttons[key] = btn

        # Bottom spacer + version
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        version = ctk.CTkLabel(
            self,
            text="v1.0",
            font=ctk.CTkFont(size=10),
            text_color="#45475a",
        )
        version.pack(pady=(0, 15), padx=15, anchor="w")

    def _on_click(self, page_key):
        if self._on_navigate:
            self._on_navigate(page_key)

    def set_active(self, page_key):
        self._active_page = page_key
        for key, btn in self._buttons.items():
            if key == page_key:
                btn.configure(fg_color=self.COLOR_ACTIVE)
            else:
                btn.configure(fg_color="transparent")
