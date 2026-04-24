"""Status bar widget for the MapProxy GUI."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from .theme import DEFAULT_THEME, GuiTheme


class StatusBar:
    """Small status row that can be updated later by the controller."""

    def __init__(self, parent: tk.Widget, theme: GuiTheme = DEFAULT_THEME) -> None:
        self.theme = theme
        self.frame = ttk.Frame(parent, style="App.TFrame")

        ttk.Label(self.frame, text="Status:", style="Body.TLabel").pack(side="left")
        self.value_label = ttk.Label(
            self.frame,
            text="Idle",
            style="Body.TLabel",
            foreground=self.theme.accent,
        )
        self.value_label.pack(side="left", padx=(8, 0))

    def set_status(self, value: str) -> None:
        self.value_label.configure(text=value)
