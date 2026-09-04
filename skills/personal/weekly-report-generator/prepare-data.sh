#!/bin/bash
#
# Tech Support Weekly Report - Data Preparation Only
# Steps: Database → Markdown issue list → GitLab API → Time Classification
# Report generation is handled by Claude Code
#
# Usage: ./prepare-data.sh [--days N] [--date YYYY-MM-DD] [--output DIR]
#

set -e  # Exit on error

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
DAYS=7
TEMP_DIR="/tmp/weekly-report-$(date +%Y%m%d)"
OUTPUT_DIR="${WEEKLY_REPORT_OUTPUT_DIR:-$HOME/Documents/Obsidian/05-Work/weekly}"
VERBOSE=true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --days)
            DAYS="$2"
            shift 2
            ;;
        --date)
            REPORT_DATE="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --quiet)
            VERBOSE=false
            shift
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Helper function for logging
log() {
    if [ "$VERBOSE" = true ]; then
        echo -e "${GREEN}[INFO]${NC} $1"
    fi
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

# Create temp directory
mkdir -p "$TEMP_DIR"

log "Starting Tech Support Weekly Report Data Preparation"
log "Temp directory: $TEMP_DIR"
log "Issue date range: Previous natural week (Asia/Shanghai)"
log "Note history window: Last $DAYS days"
if [ -n "$REPORT_DATE" ]; then
    log "Report date: $REPORT_DATE"
fi
echo ""

# Step 1: Query database for issues
log "Step 1/4: Querying database for issues..."
QUERY_ARGS=(--output "$TEMP_DIR/01-issues.json")
if [ -n "${REPORT_DATE:-}" ]; then
    QUERY_ARGS+=(--date "$REPORT_DATE")
fi
python3 "$SCRIPT_DIR/query-tech-support-issues/implementation.py" "${QUERY_ARGS[@]}" \
    || error "Failed to query database"

ISSUE_COUNT=$(jq '[.items[].issue_id] | unique | length' "$TEMP_DIR/01-issues.json" 2>/dev/null || echo "0")
log "Found $ISSUE_COUNT issues"

# Step 2: Render Markdown issue list
log "Step 2/4: Rendering Markdown issue list..."
python3 "$SCRIPT_DIR/render-weekly-issue-list/implementation.py" \
    --input "$TEMP_DIR/01-issues.json" \
    --output-dir "$OUTPUT_DIR" \
    || error "Failed to render issue list"

if [ "$ISSUE_COUNT" = "0" ]; then
    echo ""
    echo -e "${YELLOW}[WARNING]${NC} No issues found in the specified time range."
    echo "Use --date to select a different previous natural week."
    exit 0
fi
echo ""

# Step 3: Fetch GitLab issue details
log "Step 3/4: Fetching GitLab issue details..."
python3 "$SCRIPT_DIR/fetch-gitlab-issue-details/implementation.py" \
    --input "$TEMP_DIR/01-issues.json" \
    --output "$TEMP_DIR/02-issue-details.json" \
    || error "Failed to fetch GitLab details"

log "Fetched details for $ISSUE_COUNT issues"
echo ""

# Step 4: Split notes by time
log "Step 4/4: Classifying notes by time..."
python3 "$SCRIPT_DIR/split-issue-notes-by-time/implementation.py" \
    --days $DAYS \
    --input "$TEMP_DIR/02-issue-details.json" \
    --output "$TEMP_DIR/03-classified-issues.json" \
    || error "Failed to classify notes"

# Count notes
CURRENT_NOTES=$(jq '[.items[].本周工作 | length] | add' "$TEMP_DIR/03-classified-issues.json" 2>/dev/null || echo "0")
HISTORY_NOTES=$(jq '[.items[].历史回顾 | length] | add' "$TEMP_DIR/03-classified-issues.json" 2>/dev/null || echo "0")

log "Notes classified:"
echo "  - 本周工作: $CURRENT_NOTES notes"
echo "  - 历史回顾: $HISTORY_NOTES notes"
echo ""

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Data Preparation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Data file ready: $TEMP_DIR/03-classified-issues.json"
echo "Issue list saved to: $OUTPUT_DIR/weekly_issue_list_*.md"
echo ""
echo -e "${CYAN}Next step:${NC} Claude Code will read the data and generate the report."
echo ""
