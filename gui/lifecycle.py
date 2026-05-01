"""Process lifecycle management for MapProxy."""

from __future__ import annotations

import io
import os
import subprocess
import sys
import threading
from pathlib import Path
from queue import Empty, Queue


class LogCapture(io.StringIO):
    """Capture output to a queue instead of a file."""

    def __init__(self, log_queue: Queue[str]) -> None:
        super().__init__()
        self.log_queue = log_queue

    def write(self, s: str) -> int:
        """Write to queue and return bytes written."""
        if s:
            self.log_queue.put(s)
        return len(s)

    def flush(self) -> None:
        """No-op for compatibility."""
        pass


class MapProxyProcessManager:
    """Start/stop/restart the MapProxy launcher and capture logs."""

    def __init__(
        self, project_root: Path, host: str = "127.0.0.1", port: int = 8080
    ) -> None:
        self.project_root = project_root
        self.host = host
        self.port = port
        self._process: subprocess.Popen[str] | None = None
        self._server_thread: threading.Thread | None = None
        self._log_queue: Queue[str] = Queue()
        self._reader_thread: threading.Thread | None = None
        self._stop_server = False

    @property
    def service_url(self) -> str:
        return f"http://{self.host}:{self.port}/service?"

    def is_running(self) -> bool:
        # Check subprocess mode
        if self._process is not None and self._process.poll() is None:
            return True
        # Check direct thread mode
        if self._server_thread is not None and self._server_thread.is_alive():
            return True
        return False

    def start(self) -> tuple[bool, str]:
        if self.is_running():
            return False, "MapProxy is already running."

        # In PyInstaller bundles, import and run directly
        # In development, use subprocess
        if getattr(sys, "frozen", False):
            return self._start_direct()
        else:
            return self._start_subprocess()

    def _start_direct(self) -> tuple[bool, str]:
        """Start MapProxy in a background thread (for bundled/frozen app)."""
        try:
            # Import here to avoid issues in subprocess mode
            from gui.start_mapproxy_server import run_server

            self._stop_server = False
            self._server_thread = threading.Thread(
                target=self._run_server_thread,
                daemon=False,
            )
            self._server_thread.start()
            return True, f"Starting MapProxy at {self.service_url}"
        except Exception as e:
            return False, f"Failed to start MapProxy: {e}"

    def _run_server_thread(self) -> None:
        """Run the server in a thread with stdout captured to log queue."""
        # Capture stdout to log panel
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        try:
            # Redirect stdout and stderr to log queue
            sys.stdout = LogCapture(self._log_queue)
            sys.stderr = LogCapture(self._log_queue)

            from gui.start_mapproxy_server import run_server

            run_server(
                host=self.host,
                port=self.port,
                project_root=self.project_root,
                stop_event_check=lambda: self._stop_server,
            )
        except Exception as e:
            self._log_queue.put(f"[server] Error: {e}\n")
        finally:
            # Restore stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr

    def _start_subprocess(self) -> tuple[bool, str]:
        """Start MapProxy as a subprocess (for development)."""
        launcher = self.project_root / "gui" / "start-mapproxy.py"
        if not launcher.exists():
            return False, f"Missing launcher: {launcher}"

        env = os.environ.copy()
        env["MAPPROXY_HOST"] = self.host
        env["MAPPROXY_PORT"] = str(self.port)
        env["MAPPROXY_PROJECT_ROOT"] = str(self.project_root)

        try:
            self._process = subprocess.Popen(
                [sys.executable, "-u", str(launcher)],
                cwd=str(self.project_root),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )

            self._reader_thread = threading.Thread(
                target=self._read_output, daemon=True
            )
            self._reader_thread.start()
            return True, f"Starting MapProxy at {self.service_url}"
        except Exception as e:
            return False, f"Failed to start process: {e}"

    def stop(self) -> tuple[bool, str]:
        if not self.is_running():
            return False, "MapProxy is not running."

        # Stop thread-based server
        if self._server_thread is not None and self._server_thread.is_alive():
            self._stop_server = True
            self._server_thread.join(timeout=5)
            self._server_thread = None
            return True, "MapProxy stopped."

        # Stop subprocess-based server
        if self._process is not None and self._process.poll() is None:
            self._process.terminate()
            try:
                self._process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._process.kill()
                self._process.wait(timeout=5)
            self._process = None
            return True, "MapProxy stopped."

        return False, "Could not stop MapProxy."

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
