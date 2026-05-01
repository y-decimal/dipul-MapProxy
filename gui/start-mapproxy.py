#!/usr/bin/env python3
"""Minimal MapProxy launcher used by the GUI lifecycle manager."""

import argparse
import os
import sys
from pathlib import Path

# Import the server logic
from start_mapproxy_server import get_project_root, run_server


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

    project_root = None
    if "MAPPROXY_PROJECT_ROOT" in os.environ:
        project_root = Path(os.environ["MAPPROXY_PROJECT_ROOT"])

    run_server(
        host=args.host,
        port=args.port,
        project_root=project_root,
    )


if __name__ == "__main__":
    main()
