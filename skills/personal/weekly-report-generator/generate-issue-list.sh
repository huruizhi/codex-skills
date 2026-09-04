#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT_DIR="${WEEKLY_REPORT_OUTPUT_DIR:-$HOME/Documents/Obsidian/05-Work/weekly}"
QUERY_ARGS=()

while [[ $# -gt 0 ]]; do
    case "$1" in
        --date)
            QUERY_ARGS+=(--date "$2")
            shift 2
            ;;
        --start-date)
            QUERY_ARGS+=(--start-date "$2")
            shift 2
            ;;
        --end-date)
            QUERY_ARGS+=(--end-date "$2")
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

TEMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/weekly-issue-list.XXXXXX")"
trap 'rm -rf "$TEMP_DIR"' EXIT

python3 "$SCRIPT_DIR/query-tech-support-issues/implementation.py" \
    "${QUERY_ARGS[@]}" \
    --output "$TEMP_DIR/issues.json"

python3 "$SCRIPT_DIR/render-weekly-issue-list/implementation.py" \
    --input "$TEMP_DIR/issues.json" \
    --output-dir "$OUTPUT_DIR"
