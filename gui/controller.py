"""GUI controller that wires lifecycle actions to widgets."""

from __future__ import annotations

import webbrowser
from pathlib import Path
from typing import TYPE_CHECKING

from .lifecycle import MapProxyProcessManager

if TYPE_CHECKING:
    from .app import MapProxyGuiApp


class GuiController:
    """Connect UI widgets to process lifecycle and log streaming."""

    def __init__(self, app: "MapProxyGuiApp", project_root: Path) -> None:
        self.app = app
        self.manager = MapProxyProcessManager(project_root)
        self._last_running = False

        self.app.control_bar.set_callbacks(
            on_start=self.start_server,
            on_stop=self.stop_server,
            on_restart=self.restart_server,
            on_open_url=self.open_service_url,
        )
        self.app.root.protocol("WM_DELETE_WINDOW", self.on_close)

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

    def open_service_url(self) -> None:
        url = self.manager.service_url
        webbrowser.open(url)
        self.app.log_panel.write(f"[gui] Opened {url}\n")

    def on_close(self) -> None:
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
