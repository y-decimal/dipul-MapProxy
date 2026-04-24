#!/usr/bin/env python3
"""
Cross-platform MapProxy startup script for Windows and Linux.
Handles venv setup, port checking, and launching the MapProxy WSGI server.
"""

import os
import sys
import socket
import subprocess
import argparse
from pathlib import Path
from wsgiref.simple_server import make_server


def log(message):
    """Print a log message with the script prefix."""
    print(f"[start-mapproxy] {message}")


def is_port_in_use(port):
    """Check if a port is already in use (cross-platform)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        result = s.connect_ex(("127.0.0.1", port))
        return result == 0


def get_venv_python():
    """Get the path to the Python executable in the venv."""
    venv_dir = Path(".venv")
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "python.exe"
    else:
        return venv_dir / "bin" / "python"


def get_venv_mapproxy_util():
    """Get the path to the mapproxy-util executable in the venv."""
    venv_dir = Path(".venv")
    if sys.platform == "win32":
        return venv_dir / "Scripts" / "mapproxy-util.exe"
    else:
        return venv_dir / "bin" / "mapproxy-util"


def setup_venv():
    """Create venv and install dependencies if not already done."""
    venv_python = get_venv_python()
    venv_util = get_venv_mapproxy_util()

    if venv_util.exists():
        return  # venv already set up

    log("Missing virtual environment")
    log("Creating venv and installing dependencies from requirements.txt")

    venv_dir = Path(".venv")
    subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True)

    # Install packages in the venv
    subprocess.run(
        [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], check=True
    )
    subprocess.run(
        [str(venv_python), "-m", "pip", "install", "-r", "requirements.txt"],
        check=True,
    )


def ensure_running_in_venv():
    """Re-exec this script with the venv Python if needed."""
    venv_python = get_venv_python().resolve()
    current_python = Path(sys.executable).resolve()

    # Windows paths are case-insensitive, so normalize before comparing.
    same_python = os.path.normcase(str(current_python)) == os.path.normcase(
        str(venv_python)
    )
    if same_python:
        return

    os.execv(
        str(venv_python),
        [str(venv_python), str(Path(__file__).resolve()), *sys.argv[1:]],
    )


def get_local_ip():
    """Get the local IP address (cross-platform)."""
    try:
        # Connect to an external address to determine the local IP
        # This doesn't actually establish a connection
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            return local_ip
    except Exception:
        return None


def main():
    parser = argparse.ArgumentParser(
        description="Start MapProxy server (cross-platform)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment variables:
  MAPPROXY_HOST    Server bind address (default: 127.0.0.1)
  MAPPROXY_PORT    Server port (default: 8080)

Examples:
  %(prog)s
  %(prog)s --host 0.0.0.0 --port 9000
  MAPPROXY_HOST=0.0.0.0 MAPPROXY_PORT=9000 %(prog)s
        """,
    )
    parser.add_argument(
        "--host",
        default=os.getenv("MAPPROXY_HOST", "127.0.0.1"),
        help="Server bind address (default: 127.0.0.1)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("MAPPROXY_PORT", "8080")),
        help="Server port (default: 8080)",
    )

    args = parser.parse_args()
    host = args.host
    port = args.port

    # Change to script directory
    script_dir = Path(__file__).parent.resolve()
    os.chdir(script_dir)

    # Check if port is already in use
    if is_port_in_use(port):
        log(f"Port {port} is already in use.")
        log("Stop the existing process or set MAPPROXY_PORT to another free port.")
        sys.exit(1)

    # Set up venv if needed
    setup_venv()

    # Always run in the venv interpreter so installed packages are importable.
    ensure_running_in_venv()

    # Set environment variables for the server
    os.environ["MAPPROXY_HOST"] = host
    os.environ["MAPPROXY_PORT"] = str(port)

    log(f"Starting MapProxy at http://{host}:{port}/service?")
    log("Press Ctrl+C to stop")

    if host == "0.0.0.0":
        local_ip = get_local_ip()
        log("For iNav, do not use 0.0.0.0 as the URL.")
        log(f"Use http://127.0.0.1:{port}/service? if iNav runs on this machine.")
        if local_ip:
            log(
                f"Use http://{local_ip}:{port}/service? if iNav runs on another device on your LAN."
            )

    # Import mapproxy app and start the server
    from mapproxy.wsgiapp import make_wsgi_app

    app = make_wsgi_app(services_conf="mapproxy.yaml", debug=False, reloader=False)
    with make_server(host, port, app) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            log("Shutting down...")
            sys.exit(0)


if __name__ == "__main__":
    main()
