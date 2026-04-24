#!/usr/bin/env python3
"""Minimal MapProxy launcher used by the GUI lifecycle manager."""

import argparse
import os
import socket
import sys
from pathlib import Path
from wsgiref.simple_server import make_server


SCRIPT_DIR = Path(__file__).parent.resolve()
MAPPROXY_YAML = SCRIPT_DIR / "mapproxy_config" / "mapproxy.yaml"


def log(message: str) -> None:
    print(f"[start-mapproxy] {message}")


def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("127.0.0.1", port)) == 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start MapProxy server")
    parser.add_argument(
        "--host",
        default=os.getenv("MAPPROXY_HOST", "127.0.0.1"),
        help="Server bind address",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.getenv("MAPPROXY_PORT", "8080")),
        help="Server port",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    host = args.host
    port = args.port

    os.chdir(SCRIPT_DIR)

    if not MAPPROXY_YAML.exists():
        log(f"Missing config: {MAPPROXY_YAML}")
        sys.exit(1)

    if is_port_in_use(port):
        log(f"Port {port} is already in use.")
        sys.exit(1)

    from mapproxy.wsgiapp import make_wsgi_app

    log(f"Starting MapProxy at http://{host}:{port}/service?")
    app = make_wsgi_app(services_conf=str(MAPPROXY_YAML), debug=False, reloader=False)

    with make_server(host, port, app) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            log("Shutting down...")


if __name__ == "__main__":
    main()
