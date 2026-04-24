"""Barebones tkinter GUI shell for the MapProxy launcher."""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from pathlib import Path

from .control_bar import ControlBar
from .log_panel import LogPanel
from .status_bar import StatusBar
from .theme import DEFAULT_THEME, GuiTheme


class MapProxyGuiApp:
    """Small GUI shell with a status area and a log panel."""

    def __init__(self, theme: GuiTheme = DEFAULT_THEME) -> None:
        self.theme = theme
        self.root = tk.Tk()
        self.root.title("DiPul MapProxy")
        self.root.configure(bg=self.theme.window_bg)
        self.root.minsize(720, 420)

        self._configure_styles()
        self._build_ui()

    def _configure_styles(self) -> None:
        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("App.TFrame", background=self.theme.window_bg)
        style.configure("Panel.TFrame", background=self.theme.panel_bg)
        style.configure(
            "Title.TLabel",
            background=self.theme.window_bg,
            foreground=self.theme.title_fg,
            font=(self.theme.font_family, self.theme.title_size, "bold"),
        )
        style.configure(
            "Body.TLabel",
            background=self.theme.window_bg,
            foreground=self.theme.text_fg,
            font=(self.theme.font_family, self.theme.body_size),
        )
        style.configure(
            "Muted.TLabel",
            background=self.theme.window_bg,
            foreground=self.theme.muted_fg,
            font=(self.theme.font_family, self.theme.body_size),
        )

    def _build_ui(self) -> None:
        outer = ttk.Frame(self.root, style="App.TFrame", padding=18)
        outer.pack(fill="both", expand=True)

        header = ttk.Frame(outer, style="App.TFrame")
        header.pack(fill="x")

        ttk.Label(header, text="DiPul MapProxy", style="Title.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="MapProxy launcher and status dashboard",
            style="Muted.TLabel",
        ).pack(anchor="w", pady=(4, 0))

        self.status_bar = StatusBar(outer, self.theme)
        self.status_bar.frame.pack(fill="x", pady=(18, 10))

        self.control_bar = ControlBar(outer, self.theme)
        self.control_bar.frame.pack(fill="x", pady=(0, 10))

        self.log_panel = LogPanel(outer, self.theme)
        self.log_panel.frame.pack(fill="both", expand=True)

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    from .controller import GuiController

    app = MapProxyGuiApp()
    GuiController(app, project_root=Path(__file__).resolve().parent.parent)
    app.run()


if __name__ == "__main__":
    main()
