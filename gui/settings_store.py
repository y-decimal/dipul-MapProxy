"""Persisted GUI settings."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass
class GuiSettings:
    close_to_tray_on_close: bool = False


class SettingsStore:
    """Load and save GUI settings from a small JSON file."""

    def __init__(self, settings_file: Path) -> None:
        self.settings_file = settings_file

    def load(self) -> GuiSettings:
        if not self.settings_file.exists():
            return GuiSettings()

        try:
            raw = json.loads(self.settings_file.read_text(encoding="utf-8"))
        except Exception:
            return GuiSettings()

        return GuiSettings(
            close_to_tray_on_close=bool(raw.get("close_to_tray_on_close", False))
        )

    def save(self, settings: GuiSettings) -> None:
        self.settings_file.write_text(
            json.dumps(asdict(settings), indent=2),
            encoding="utf-8",
        )
