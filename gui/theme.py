"""Theme values for the MapProxy GUI.

Keep this small so colors and typography can be adjusted later without
rewriting the window layout.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class GuiTheme:
    window_bg: str = "#111827"
    panel_bg: str = "#1f2937"
    text_bg: str = "#0f172a"
    text_fg: str = "#e5e7eb"
    title_fg: str = "#f9fafb"
    accent: str = "#38bdf8"
    muted_fg: str = "#9ca3af"
    font_family: str = "Segoe UI"
    title_size: int = 18
    body_size: int = 10


DEFAULT_THEME = GuiTheme()
