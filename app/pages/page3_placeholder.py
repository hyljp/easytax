import customtkinter as ctk
from app.pages.base_page import BasePage


class Page3(BasePage):
    def __init__(self, parent):
        super().__init__(parent)
        label = ctk.CTkLabel(
            self,
            text="Page 3\n（準備中）",
            font=ctk.CTkFont(size=24),
            text_color="#888888",
        )
        label.place(relx=0.5, rely=0.5, anchor="center")
