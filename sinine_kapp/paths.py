"""Shared filesystem paths used by the kiosk app."""

from pathlib import Path


# Keep path construction centralized so launch scripts, tools, and modules can
# move together if the repo root changes.
PACKAGE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = PACKAGE_ROOT.parent
ASSETS_DIR = PROJECT_ROOT / "assets"
DOCS_DIR = PROJECT_ROOT / "docs"
TOOLS_DIR = PROJECT_ROOT / "tools"
LOG_FILE = PROJECT_ROOT / "main.log"
ENV_FILE = PROJECT_ROOT / ".env"
