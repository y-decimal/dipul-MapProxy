"""System tray integration for minimize-to-tray behavior."""

from __future__ import annotations

import threading
from typing import Callable


RestoreCallback = Callable[[], None]
ExitCallback = Callable[[], None]


class TrayManager:
    """Wrap pystray usage behind a minimal interface."""

    def __init__(self, on_restore: RestoreCallback, on_exit: ExitCallback) -> None:
        self._on_restore = on_restore
        self._on_exit = on_exit
        self._icon = None
        self._thread: threading.Thread | None = None
        self._available = False
        self._availability_error: str | None = None

        try:
            import pystray  # noqa: F401
            from PIL import Image  # noqa: F401

            self._available = True
        except Exception as exc:
            self._available = False
            self._availability_error = str(exc)

    @property
    def available(self) -> bool:
        return self._available

    @property
    def unavailable_reason(self) -> str:
        if self._availability_error:
            return self._availability_error
        return "missing tray dependencies"

    def show(self) -> bool:
        if not self.available:
            return False
        if self._icon is not None:
            return True

        import pystray
        from PIL import Image, ImageDraw

        def restore_action(_icon, _item) -> None:
            self._on_restore()

        def exit_action(_icon, _item) -> None:
            self._on_exit()

        image = Image.new("RGB", (64, 64), color=(22, 33, 62))
        draw = ImageDraw.Draw(image)
        draw.rectangle((12, 12, 52, 52), outline=(56, 189, 248), width=5)

        menu = pystray.Menu(
            pystray.MenuItem("Restore", restore_action, default=True),
            pystray.MenuItem("Exit", exit_action),
        )

        self._icon = pystray.Icon("dipul-mapproxy", image, "DiPul MapProxy", menu)
        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()
        return True

    def hide(self) -> None:
        if self._icon is None:
            return
        self._icon.stop()
        self._icon = None
        self._thread = None
