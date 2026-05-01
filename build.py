#!/usr/bin/env python3
"""
Build script for creating DiPul MapProxy binaries.

Usage:
    python build.py --platform windows  # Windows exe
    python build.py --platform linux    # Linux executable + AppImage
    python build.py --platform all      # All available platforms for current OS
"""

import argparse
import sys
import subprocess
import tempfile
from pathlib import Path
import shutil
import platform

PROJECT_ROOT = Path(__file__).resolve().parent
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
SPEC_FILE = PROJECT_ROOT / "dipul_mapproxy.spec"


def run_command(cmd, check=True, **kwargs):
    """Run a shell command and return the result."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, check=check, shell=False, **kwargs)
    return result


def get_pyinstaller_cmd():
    """Get the appropriate PyInstaller command for the current environment."""
    # Try to use python -m PyInstaller for better venv compatibility
    return [sys.executable, "-m", "PyInstaller"]


def clean_build():
    """Remove build artifacts."""
    print("Cleaning previous build artifacts...")
    for directory in [BUILD_DIR, DIST_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
            print(f"  Removed {directory}")


def check_dependencies():
    """Check if PyInstaller is installed."""
    try:
        import PyInstaller

        print(f"✓ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print(
            "✗ PyInstaller not found. Install with: pip install -r build_requirements.txt"
        )
        sys.exit(1)


def build_windows():
    """Build Windows executable."""
    print("\n=== Building Windows executable ===")
    if platform.system() != "Windows":
        print("Warning: Cross-compiling for Windows from non-Windows system.")
        print("  This may result in missing Windows-specific dependencies.")

    cmd = get_pyinstaller_cmd() + [
        str(SPEC_FILE),
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(BUILD_DIR),
        "--clean",
    ]

    run_command(cmd)

    exe_path = DIST_DIR / "dipul-mapproxy.exe"
    if exe_path.exists():
        print(f"✓ Windows executable created: {exe_path}")
        return exe_path
    else:
        print(f"✗ Failed to create Windows executable")
        return None


def build_linux():
    """Build Linux executable and AppImage."""
    print("\n=== Building Linux executable ===")
    if platform.system() != "Linux":
        print("Error: Linux build requires running on Linux")
        return None

    cmd = get_pyinstaller_cmd() + [
        str(SPEC_FILE),
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(BUILD_DIR),
        "--clean",
    ]

    run_command(cmd)

    exe_path = DIST_DIR / "dipul-mapproxy"
    if exe_path.exists():
        print(f"✓ Linux executable created: {exe_path}")
        # Make executable
        exe_path.chmod(0o755)
        return exe_path
    else:
        print(f"✗ Failed to create Linux executable")
        return None


def build_appimage(exe_path):
    """Create an AppImage from the built executable (Linux only)."""
    print("\n=== Creating AppImage ===")

    # Check if appimagetool is available
    result = run_command(["which", "appimagetool"], check=False, capture_output=True)
    if result.returncode != 0:
        print("⚠ appimagetool not found. Skipping AppImage creation.")
        print("  Install with: apt install appimage-builder (Ubuntu/Debian)")
        return None

    # For now, just document that AppImage is an option
    print("ℹ AppImage creation requires additional setup. See docs/BUILD.md")
    return None


def build_macos():
    """Build macOS executable."""
    print("\n=== Building macOS executable ===")
    if platform.system() != "Darwin":
        print("Error: macOS build requires running on macOS")
        return None

    cmd = get_pyinstaller_cmd() + [
        str(SPEC_FILE),
        "--distpath",
        str(DIST_DIR),
        "--workpath",
        str(BUILD_DIR),
        "--clean",
    ]

    run_command(cmd)

    exe_path = DIST_DIR / "dipul-mapproxy"
    if exe_path.exists():
        print(f"✓ macOS executable created: {exe_path}")
        exe_path.chmod(0o755)
        return exe_path
    else:
        print(f"✗ Failed to create macOS executable")
        return None


def main():
    parser = argparse.ArgumentParser(description="Build DiPul MapProxy binaries")
    parser.add_argument(
        "--platform",
        choices=["windows", "linux", "macos", "all"],
        default="all",
        help="Target platform(s). 'all' builds for current OS.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean build artifacts before building",
    )
    parser.add_argument(
        "--skip-clean",
        action="store_true",
        help="Don't clean build artifacts",
    )

    args = parser.parse_args()

    check_dependencies()

    if args.clean and not args.skip_clean:
        clean_build()

    system = platform.system()
    targets = []

    if args.platform == "all":
        if system == "Windows":
            targets = ["windows"]
        elif system == "Linux":
            targets = ["linux"]
        elif system == "Darwin":
            targets = ["macos"]
    else:
        targets = [args.platform]

    results = {}

    for target in targets:
        if target == "windows":
            results["windows"] = build_windows()
        elif target == "linux":
            results["linux"] = build_linux()
        elif target == "macos":
            results["macos"] = build_macos()

    print("\n=== Build Summary ===")
    for target, path in results.items():
        status = "✓" if path else "✗"
        print(f"{status} {target}: {path if path else 'FAILED'}")

    # Exit with error if any build failed
    if any(v is None for v in results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
