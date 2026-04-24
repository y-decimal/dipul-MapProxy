"""Control bar widget for lifecycle actions."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from .theme import DEFAULT_THEME, GuiTheme


Callback = Callable[[], None]


class ControlBar:
    """Action buttons for starting/stopping/restarting the server."""

    def __init__(self, parent: tk.Widget, theme: GuiTheme = DEFAULT_THEME) -> None:
        self.theme = theme
        self.frame = ttk.Frame(parent, style="App.TFrame")

        self.start_button = ttk.Button(self.frame, text="Start")
        self.stop_button = ttk.Button(self.frame, text="Stop")
        self.restart_button = ttk.Button(self.frame, text="Restart")
        self.copy_url_button = ttk.Button(self.frame, text="Copy URL")
        self.settings_button = ttk.Button(self.frame, text="Settings")

        self.start_button.pack(side="left")
        self.stop_button.pack(side="left", padx=(8, 0))
        self.restart_button.pack(side="left", padx=(8, 0))
        self.copy_url_button.pack(side="left", padx=(8, 0))
        self.settings_button.pack(side="left", padx=(8, 0))

        self.set_running_state(False)

    def set_callbacks(
        self,
        on_start: Callback,
        on_stop: Callback,
        on_restart: Callback,
        on_copy_url: Callback,
        on_settings: Callback,
    ) -> None:
        self.start_button.configure(command=on_start)
        self.stop_button.configure(command=on_stop)
        self.restart_button.configure(command=on_restart)
        self.copy_url_button.configure(command=on_copy_url)
        self.settings_button.configure(command=on_settings)

    def set_running_state(self, running: bool) -> None:
        if running:
            self.start_button.configure(state="disabled")
            self.stop_button.configure(state="normal")
            self.restart_button.configure(state="normal")
            self.copy_url_button.configure(state="normal")
        else:
            self.start_button.configure(state="normal")
            self.stop_button.configure(state="disabled")
            self.restart_button.configure(state="disabled")
            self.copy_url_button.configure(state="disabled")
