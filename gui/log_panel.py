"""Log panel widget for the MapProxy GUI."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .theme import DEFAULT_THEME, GuiTheme


class LogPanel:
    """Scrollable text area intended for dynamic log output."""

    def __init__(self, parent: tk.Widget, theme: GuiTheme = DEFAULT_THEME) -> None:
        self.theme = theme
        self.frame = ttk.Frame(parent, style="Panel.TFrame", padding=12)

        ttk.Label(
            self.frame,
            text="Logs",
            background=self.theme.panel_bg,
            foreground=self.theme.text_fg,
            font=(self.theme.font_family, self.theme.body_size, "bold"),
        ).pack(anchor="w")

        self.text = tk.Text(
            self.frame,
            height=12,
            wrap="word",
            bg=self.theme.text_bg,
            fg=self.theme.text_fg,
            insertbackground=self.theme.text_fg,
            relief="flat",
            borderwidth=0,
            font=(self.theme.font_family, self.theme.body_size),
        )
        self.text.pack(fill="both", expand=True, pady=(10, 0))
        self.write(
            "GUI shell ready.\n\n"
            "This first phase only establishes the window layout and style hooks.\n"
            "Server lifecycle and live log streaming will be added next.\n"
        )

    def write(self, message: str) -> None:
        self.text.configure(state="normal")
        self.text.insert("end", message)
        self.text.see("end")
        self.text.configure(state="disabled")
