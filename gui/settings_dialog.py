"""Settings dialog UI."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from .settings_store import GuiSettings
from .theme import DEFAULT_THEME, GuiTheme


SaveCallback = Callable[[GuiSettings], None]


class SettingsDialog:
    """Small settings dialog with extension space for future options."""

    def __init__(
        self,
        parent: tk.Tk,
        current: GuiSettings,
        on_save: SaveCallback,
        theme: GuiTheme = DEFAULT_THEME,
    ) -> None:
        self._on_save = on_save
        self._theme = theme
        self._window = tk.Toplevel(parent)
        self._window.title("Settings")
        self._window.resizable(False, False)
        self._window.transient(parent)
        self._window.grab_set()
        self._window.configure(bg=self._theme.window_bg)

        self._configure_styles()

        self._close_to_tray_var = tk.BooleanVar(value=current.close_to_tray_on_close)

        outer = ttk.Frame(self._window, style="App.TFrame", padding=14)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="General", style="SettingsHeader.TLabel").pack(anchor="w")
        ttk.Checkbutton(
            outer,
            text="Clicking X minimizes to task tray",
            variable=self._close_to_tray_var,
            style="Settings.TCheckbutton",
        ).pack(anchor="w", pady=(8, 0))

        ttk.Label(
            outer,
            text="Minimize button always minimizes to tray.",
            style="Body.TLabel",
        ).pack(anchor="w", pady=(8, 0))

        ttk.Separator(outer, orient="horizontal").pack(fill="x", pady=12)
        ttk.Label(
            outer,
            text="More settings will be added here in future releases.",
            style="Muted.TLabel",
        ).pack(anchor="w")

        actions = ttk.Frame(outer, style="App.TFrame")
        actions.pack(fill="x", pady=(14, 0))

        ttk.Button(actions, text="Cancel", command=self._window.destroy).pack(
            side="right"
        )
        ttk.Button(actions, text="Save", command=self._save).pack(
            side="right", padx=(0, 8)
        )

    def _save(self) -> None:
        self._on_save(GuiSettings(close_to_tray_on_close=self._close_to_tray_var.get()))
        self._window.destroy()

    def _configure_styles(self) -> None:
        style = ttk.Style(self._window)
        style.configure(
            "SettingsHeader.TLabel",
            background=self._theme.window_bg,
            foreground=self._theme.title_fg,
            font=(self._theme.font_family, self._theme.body_size, "bold"),
        )
        style.configure(
            "Settings.TCheckbutton",
            background=self._theme.window_bg,
            foreground=self._theme.text_fg,
            font=(self._theme.font_family, self._theme.body_size),
        )
        style.map(
            "Settings.TCheckbutton",
            background=[("active", self._theme.window_bg)],
            foreground=[("active", self._theme.text_fg)],
        )
