import tkinter as tk
import customtkinter as ctk
from PIL import Image


class ImageViewer(ctk.CTkFrame):
    def __init__(self, parent, on_folder_selected=None, on_prev=None, on_next=None, on_rotate=None, on_zoom_in=None, on_zoom_out=None):
        super().__init__(parent, fg_color="transparent")

        self._on_folder_selected = on_folder_selected
        self._on_prev = on_prev
        self._on_next = on_next
        self._on_rotate = on_rotate
        self._on_zoom_in = on_zoom_in
        self._on_zoom_out = on_zoom_out

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Top bar: folder button + path label + counter
        top_bar = ctk.CTkFrame(self, fg_color="transparent")
        top_bar.grid(row=0, column=0, sticky="ew", padx=5, pady=(5, 2))
        top_bar.grid_columnconfigure(1, weight=1)

        self.folder_btn = ctk.CTkButton(
            top_bar,
            text="📁 画像フォルダを選択",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=190,
            height=36,
            corner_radius=10,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            border_width=1,
            border_color="#60a5fa",
            command=self._folder_click,
        )
        self.folder_btn.grid(row=0, column=0, padx=(0, 10))

        self.path_label = ctk.CTkLabel(
            top_bar,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#a6adc8",
            anchor="w",
        )
        self.path_label.grid(row=0, column=1, sticky="w")

        self.counter_label = ctk.CTkLabel(
            top_bar,
            text="",
            font=ctk.CTkFont(size=12),
            text_color="#7f849c",
        )
        self.counter_label.grid(row=0, column=2, padx=(10, 0))

        # Canvas area with border
        canvas_frame = ctk.CTkFrame(self, fg_color="#1e1e2e", corner_radius=8)
        canvas_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(canvas_frame, bg="#181825", highlightthickness=0)
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=2, pady=2)

        # Bottom nav buttons
        nav_bar = ctk.CTkFrame(self, fg_color="transparent")
        nav_bar.grid(row=2, column=0, sticky="ew", padx=5, pady=(2, 5))
        nav_bar.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1)

        self.prev_btn = ctk.CTkButton(
            nav_bar,
            text="◀  前へ",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=110,
            height=36,
            corner_radius=10,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            border_width=1,
            border_color="#60a5fa",
            command=self._prev_click,
        )
        self.prev_btn.grid(row=0, column=0, padx=4)

        self.rotate_btn = ctk.CTkButton(
            nav_bar,
            text="↻ 回転",
            font=ctk.CTkFont(size=13),
            width=90,
            height=36,
            corner_radius=10,
            fg_color="#64748b",
            hover_color="#475569",
            border_width=1,
            border_color="#94a3b8",
            command=self._rotate_click,
        )
        self.rotate_btn.grid(row=0, column=1, padx=4)

        self.next_btn = ctk.CTkButton(
            nav_bar,
            text="次へ  ▶",
            font=ctk.CTkFont(size=13, weight="bold"),
            width=110,
            height=36,
            corner_radius=10,
            fg_color="#3b82f6",
            hover_color="#2563eb",
            border_width=1,
            border_color="#60a5fa",
            command=self._next_click,
        )
        self.next_btn.grid(row=0, column=2, padx=4)

        # Spacer
        spacer = ctk.CTkLabel(nav_bar, text="", width=10)
        spacer.grid(row=0, column=3, padx=0)

        self.zoom_out_btn = ctk.CTkButton(
            nav_bar,
            text="－",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=40,
            height=36,
            corner_radius=8,
            fg_color="#475569",
            hover_color="#334155",
            border_width=1,
            border_color="#64748b",
            command=self._zoom_out_click,
        )
        self.zoom_out_btn.grid(row=0, column=4, padx=(4, 0))

        self.zoom_label = ctk.CTkLabel(
            nav_bar,
            text="100%",
            font=ctk.CTkFont(size=12, weight="bold"),
            width=50,
            text_color="#a6adc8",
        )
        self.zoom_label.grid(row=0, column=5, padx=0)

        self.zoom_in_btn = ctk.CTkButton(
            nav_bar,
            text="＋",
            font=ctk.CTkFont(size=16, weight="bold"),
            width=40,
            height=36,
            corner_radius=8,
            fg_color="#475569",
            hover_color="#334155",
            border_width=1,
            border_color="#64748b",
            command=self._zoom_in_click,
        )
        self.zoom_in_btn.grid(row=0, column=6, padx=(0, 4))

    def set_path_text(self, text):
        self.path_label.configure(text=text)

    def set_counter_text(self, text):
        self.counter_label.configure(text=text)

    def _folder_click(self):
        if self._on_folder_selected:
            self._on_folder_selected()

    def _prev_click(self):
        if self._on_prev:
            self._on_prev()

    def _next_click(self):
        if self._on_next:
            self._on_next()

    def _rotate_click(self):
        if self._on_rotate:
            self._on_rotate()

    def _zoom_in_click(self):
        if self._on_zoom_in:
            self._on_zoom_in()

    def _zoom_out_click(self):
        if self._on_zoom_out:
            self._on_zoom_out()

    def set_zoom_text(self, text):
        self.zoom_label.configure(text=text)
