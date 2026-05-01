"""MapProxy server runner - can be called directly or via subprocess."""

import os
import socket
import sys
import threading
from pathlib import Path
from wsgiref.simple_server import make_server
from typing import Callable, Optional


def log(message: str) -> None:
    """Log a message with server prefix."""
    print(f"[start-mapproxy] {message}", flush=True)


def get_project_root() -> Path:
    """Get project root, handling both normal and PyInstaller bundle execution."""
    if "MAPPROXY_PROJECT_ROOT" in os.environ:
        return Path(os.environ["MAPPROXY_PROJECT_ROOT"])

    if getattr(sys, "frozen", False):
        # Running from PyInstaller bundle
        return Path(sys._MEIPASS)  # type: ignore

    # Running normally
    return Path(__file__).parent.parent.resolve()


def is_port_in_use(port: int) -> bool:
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("127.0.0.1", port)) == 0


def run_server(
    host: str = "127.0.0.1",
    port: int = 8080,
    project_root: Optional[Path] = None,
    stop_event_check: Optional[Callable[[], bool]] = None,
) -> None:
    """
    Run the MapProxy server.

    Args:
        host: Server bind address
        port: Server port
        project_root: Project root directory (auto-detected if not provided)
        stop_event_check: Optional callable that returns True when server should stop
    """
    if project_root is None:
        project_root = get_project_root()

    mapproxy_yaml = project_root / "mapproxy_config" / "mapproxy.yaml"

    log(f"Project root: {project_root}")
    log(f"MapProxy config: {mapproxy_yaml}")

    os.chdir(project_root)

    if not mapproxy_yaml.exists():
        log(f"Missing config: {mapproxy_yaml}")
        sys.exit(1)

    if is_port_in_use(port):
        log(f"Port {port} is already in use.")
        sys.exit(1)

    try:
        from mapproxy.wsgiapp import make_wsgi_app
    except ImportError as e:
        log(f"Failed to import mapproxy: {e}")
        sys.exit(1)

    log(f"Starting MapProxy at http://{host}:{port}/service?")
    app = make_wsgi_app(
        services_conf=str(mapproxy_yaml),
        debug=False,
        reloader=False,
    )

    # Create server
    server = make_server(host, port, app)

    # Handle graceful shutdown
    try:
        if stop_event_check is not None:
            # Thread mode: run server with shutdown monitoring
            def shutdown_monitor():
                """Monitor stop event and shutdown server."""
                while not stop_event_check():
                    threading.Event().wait(0.5)
                server.shutdown()

            monitor = threading.Thread(target=shutdown_monitor, daemon=True)
            monitor.start()
            server.serve_forever()
        else:
            # Subprocess mode: run until interrupted
            server.serve_forever()
    except KeyboardInterrupt:
        log("Shutting down...")
    finally:
        server.server_close()
        log("Server stopped.")
