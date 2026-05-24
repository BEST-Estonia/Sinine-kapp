#!/bin/bash
set -e

PROJECT_DIR="/home/skpi/Sinine-kapp/Sinine-kapp"
cd "$PROJECT_DIR"

if [ -x "./venv/bin/python" ]; then
  PYTHON="./venv/bin/python"
else
  PYTHON="python3"
fi

exec "$PYTHON" -m sinine_kapp
