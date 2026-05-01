"""System tray integration for minimize-to-tray behavior."""

from __future__ import annotations

import platform
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

        # Disable tray on Linux due to pystray unreliability
        if platform.system() == "Linux":
            self._availability_error = "Tray support disabled on Linux (unreliable)"
            return

        # Try to import tray dependencies on other platforms
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

        try:
            import pystray
            from PIL import Image, ImageDraw

            def restore_action(_icon, _item) -> None:
                """Handle restore action from tray menu."""
                try:
                    self._on_restore()
                except Exception as e:
                    print(f"[tray] Error in restore_action: {e}")

            def exit_action(_icon, _item) -> None:
                """Handle exit action from tray menu."""
                try:
                    self._on_exit()
                except Exception as e:
                    print(f"[tray] Error in exit_action: {e}")

            # Create a simple but visible icon (blue square with white border)
            image = Image.new("RGB", (64, 64), color=(22, 33, 62))
            draw = ImageDraw.Draw(image)
            # Draw a white border and blue center
            draw.rectangle(
                (4, 4, 60, 60), fill=(56, 189, 248), outline=(255, 255, 255), width=2
            )
            # Add an "M" letter to make it more recognizable
            draw.text((24, 20), "M", fill=(22, 33, 62))

            menu = pystray.Menu(
                pystray.MenuItem("Restore", restore_action, default=True),
                pystray.MenuItem("Exit", exit_action),
            )

            self._icon = pystray.Icon(
                "dipul-mapproxy",
                image,
                "DiPul MapProxy",
                menu,
            )

            # Run icon in a daemon thread
            self._thread = threading.Thread(target=self._run_icon, daemon=True)
            self._thread.start()

            print("[tray] Tray icon created and started")
            return True
        except Exception as e:
            self._availability_error = str(e)
            print(f"[tray] Failed to create tray icon: {e}")
            return False

    def _run_icon(self) -> None:
        """Run the tray icon in a safe way."""
        if self._icon is None:
            return
        try:
            self._icon.run()
        except Exception as e:
            print(f"[tray] Error running icon: {e}")

    def hide(self) -> None:
        """Hide and stop the tray icon."""
        if self._icon is None:
            return

        try:
            self._icon.stop()
        except Exception as e:
            print(f"[tray] Error stopping icon: {e}")
        finally:
            self._icon = None
            self._thread = None
