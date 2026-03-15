import customtkinter as ctk


class BasePage(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)

    def on_show(self):
        pass

    def on_hide(self):
        pass
