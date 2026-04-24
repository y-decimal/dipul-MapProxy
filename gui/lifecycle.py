"""Process lifecycle management for MapProxy."""

from __future__ import annotations

import os
import subprocess
import sys
import threading
from pathlib import Path
from queue import Empty, Queue


class MapProxyProcessManager:
    """Start/stop/restart the MapProxy launcher and capture logs."""

    def __init__(
        self, project_root: Path, host: str = "127.0.0.1", port: int = 8080
    ) -> None:
        self.project_root = project_root
        self.host = host
        self.port = port
        self._process: subprocess.Popen[str] | None = None
        self._log_queue: Queue[str] = Queue()
        self._reader_thread: threading.Thread | None = None

    @property
    def service_url(self) -> str:
        return f"http://{self.host}:{self.port}/service?"

    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    def start(self) -> tuple[bool, str]:
        if self.is_running():
            return False, "MapProxy is already running."

        launcher = self.project_root / "start-mapproxy.py"
        if not launcher.exists():
            return False, f"Missing launcher: {launcher}"

        env = os.environ.copy()
        env["MAPPROXY_HOST"] = self.host
        env["MAPPROXY_PORT"] = str(self.port)

        self._process = subprocess.Popen(
            [sys.executable, "-u", str(launcher)],
            cwd=str(self.project_root),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        self._reader_thread = threading.Thread(target=self._read_output, daemon=True)
        self._reader_thread.start()
        return True, f"Starting MapProxy at {self.service_url}"

    def stop(self) -> tuple[bool, str]:
        if not self.is_running():
            return False, "MapProxy is not running."

        assert self._process is not None
        self._process.terminate()
        try:
            self._process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self._process.kill()
            self._process.wait(timeout=5)

        self._process = None
        return True, "MapProxy stopped."

    def restart(self) -> tuple[bool, str]:
        was_running = self.is_running()
        if was_running:
            self.stop()
        return self.start()

    def drain_logs(self) -> list[str]:
        lines: list[str] = []
        while True:
            try:
                lines.append(self._log_queue.get_nowait())
            except Empty:
                break
        return lines

    def _read_output(self) -> None:
        process = self._process
        if process is None or process.stdout is None:
            return

        for line in process.stdout:
            self._log_queue.put(line)

        exit_code = process.wait()
        self._log_queue.put(
            f"[manager] MapProxy process exited with code {exit_code}\n"
        )
