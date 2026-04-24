"""Settings dialog UI."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Callable

from .settings_store import GuiSettings


SaveCallback = Callable[[GuiSettings], None]


class SettingsDialog:
    """Small settings dialog with extension space for future options."""

    def __init__(
        self,
        parent: tk.Tk,
        current: GuiSettings,
        on_save: SaveCallback,
    ) -> None:
        self._on_save = on_save
        self._window = tk.Toplevel(parent)
        self._window.title("Settings")
        self._window.resizable(False, False)
        self._window.transient(parent)
        self._window.grab_set()

        self._close_to_tray_var = tk.BooleanVar(value=current.close_to_tray_on_close)

        outer = ttk.Frame(self._window, padding=14)
        outer.pack(fill="both", expand=True)

        ttk.Label(outer, text="General", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Checkbutton(
            outer,
            text="Clicking X minimizes to task tray",
            variable=self._close_to_tray_var,
        ).pack(anchor="w", pady=(8, 0))

        ttk.Label(
            outer,
            text="Minimize button always minimizes to tray.",
        ).pack(anchor="w", pady=(8, 0))

        ttk.Separator(outer, orient="horizontal").pack(fill="x", pady=12)
        ttk.Label(
            outer,
            text="More settings will be added here in future releases.",
        ).pack(anchor="w")

        actions = ttk.Frame(outer)
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
