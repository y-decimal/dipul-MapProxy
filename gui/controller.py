"""GUI controller that wires lifecycle actions to widgets."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from .lifecycle import MapProxyProcessManager
from .settings_dialog import SettingsDialog
from .settings_store import GuiSettings, SettingsStore
from .tray_manager import TrayManager

if TYPE_CHECKING:
    from .app import MapProxyGuiApp


class GuiController:
    """Connect UI widgets to process lifecycle and log streaming."""

    def __init__(self, app: "MapProxyGuiApp", project_root: Path) -> None:
        self.app = app
        self.manager = MapProxyProcessManager(project_root)
        self.settings_store = SettingsStore(project_root / "gui_settings.json")
        self.settings = self.settings_store.load()
        self.tray = TrayManager(
            on_restore=self.restore_from_tray,
            on_exit=self.exit_from_tray,
        )
        self._last_running = False
        self._is_exiting = False

        self.app.control_bar.set_callbacks(
            on_start=self.start_server,
            on_stop=self.stop_server,
            on_restart=self.restart_server,
            on_copy_url=self.copy_service_url,
            on_settings=self.open_settings,
        )
        self.app.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.app.root.bind("<Unmap>", self.on_window_unmap)

        self.app.status_bar.set_status("Idle")
        self.app.control_bar.set_running_state(False)
        self.app.log_panel.write("[gui] Lifecycle manager ready.\n")
        self._poll_logs()

    def start_server(self) -> None:
        ok, message = self.manager.start()
        self.app.log_panel.write(f"[gui] {message}\n")
        if ok:
            self.app.status_bar.set_status("Starting")
        self._sync_running_state()

    def stop_server(self) -> None:
        ok, message = self.manager.stop()
        self.app.log_panel.write(f"[gui] {message}\n")
        if ok:
            self.app.status_bar.set_status("Stopped")
        self._sync_running_state()

    def restart_server(self) -> None:
        ok, message = self.manager.restart()
        self.app.log_panel.write(f"[gui] {message}\n")
        if ok:
            self.app.status_bar.set_status("Starting")
        self._sync_running_state()

    def copy_service_url(self) -> None:
        url = self.manager.service_url
        self.app.root.clipboard_clear()
        self.app.root.clipboard_append(url)
        self.app.log_panel.write(f"[gui] Copied URL to clipboard: {url}\n")

    def on_close(self) -> None:
        if self.settings.close_to_tray_on_close:
            if self._minimize_to_tray():
                return
            self.app.log_panel.write(
                "[gui] Tray integration not available. Closing window.\n"
            )

        self._shutdown_app()

    def on_window_unmap(self, _event) -> None:
        if self._is_exiting:
            return
        if self.app.root.state() == "iconic":
            self._minimize_to_tray()

    def open_settings(self) -> None:
        SettingsDialog(
            parent=self.app.root,
            current=self.settings,
            on_save=self.save_settings,
            theme=self.app.theme,
        )

    def save_settings(self, settings: GuiSettings) -> None:
        self.settings = settings
        self.settings_store.save(settings)
        state = "enabled" if settings.close_to_tray_on_close else "disabled"
        self.app.log_panel.write(f"[gui] Setting updated: close-to-tray is {state}.\n")

    def restore_from_tray(self) -> None:
        self.app.root.after(0, self._restore_window)

    def exit_from_tray(self) -> None:
        self.app.root.after(0, self._exit_from_tray)

    def _restore_window(self) -> None:
        self.tray.hide()
        self.app.root.deiconify()
        self.app.root.lift()
        self.app.root.focus_force()

    def _exit_from_tray(self) -> None:
        self.tray.hide()
        self._shutdown_app()

    def _minimize_to_tray(self) -> bool:
        if not self.tray.show():
            self.app.log_panel.write(
                f"[gui] Tray integration not available: {self.tray.unavailable_reason}\n"
            )
            return False
        self.app.root.withdraw()
        self.app.log_panel.write(
            "[gui] Minimized to tray. Use tray icon to restore or exit.\n"
        )
        return True

    def _shutdown_app(self) -> None:
        self._is_exiting = True
        if self.manager.is_running():
            self.manager.stop()
        self.app.root.destroy()

    def _poll_logs(self) -> None:
        for line in self.manager.drain_logs():
            self.app.log_panel.write(line)

        self._sync_running_state()
        self.app.root.after(200, self._poll_logs)

    def _sync_running_state(self) -> None:
        running = self.manager.is_running()
        self.app.control_bar.set_running_state(running)

        if running and not self._last_running:
            self.app.status_bar.set_status("Running")
        if not running and self._last_running:
            self.app.status_bar.set_status("Stopped")
        self._last_running = running
