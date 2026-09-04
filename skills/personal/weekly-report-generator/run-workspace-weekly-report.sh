#!/usr/bin/env bash
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${WEEKLY_REPORT_OUTPUT_DIR:-$HOME/Documents/Obsidian/05-Work/weekly}"
PYTHON_BIN="${PYTHON_BIN:-python3}"

mkdir -p "$OUTPUT_DIR"
cd "$SKILL_DIR"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[ERROR] python3 not found" >&2
  exit 1
fi

if ! "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1
import mysql.connector, requests
PY
then
  echo "[INFO] installing python deps: mysql-connector-python requests"
  "$PYTHON_BIN" -m pip install mysql-connector-python requests
fi

"$SKILL_DIR/prepare-data.sh" --output "$OUTPUT_DIR" "$@"

echo "[INFO] data prepared. next: generate markdown report from /tmp/weekly-report-YYYYMMDD/03-classified-issues.json"
echo "[INFO] output dir: $OUTPUT_DIR"
