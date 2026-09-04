#!/bin/bash
#
# Tech Support Weekly Report Generator
# Complete pipeline: Database → Issue List → GitLab API → Process → LLM
#
# Usage: ./run-full-pipeline.sh [--days N] [--date YYYY-MM-DD]
#

set -e  # Exit on error

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values
DAYS=7
OUTPUT_DIR="${WEEKLY_REPORT_OUTPUT_DIR:-$HOME/Documents/Obsidian/05-Work/weekly}"
TEMP_DIR="/tmp/weekly-report-$(date +%Y%m%d)"
VERBOSE=true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

log "Starting Tech Support Weekly Report Generation"
log "Output directory: $OUTPUT_DIR"
log "Issue date range: Previous natural week (Asia/Shanghai)"
log "Note history window: Last $DAYS days"
if [ -n "$REPORT_DATE" ]; then
    log "Report date: $REPORT_DATE"
fi
echo ""

# Step 1: Query database for issues
log "Step 1/5: Querying database for issues..."
QUERY_ARGS=(--output "$TEMP_DIR/01-issues.json")
if [ -n "${REPORT_DATE:-}" ]; then
    QUERY_ARGS+=(--date "$REPORT_DATE")
fi
python3 "$SCRIPT_DIR/query-tech-support-issues/implementation.py" "${QUERY_ARGS[@]}" \
    || error "Failed to query database"

ISSUE_COUNT=$(jq '[.items[].issue_id] | unique | length' "$TEMP_DIR/01-issues.json")
log "Found $ISSUE_COUNT issues"
echo ""

# Step 2: Render Markdown issue list
log "Step 2/5: Rendering Markdown issue list..."
python3 "$SCRIPT_DIR/render-weekly-issue-list/implementation.py" \
    --input "$TEMP_DIR/01-issues.json" \
    --output-dir "$OUTPUT_DIR" \
    || error "Failed to render issue list"

if [ "$ISSUE_COUNT" = "0" ]; then
    echo -e "${YELLOW}[WARNING]${NC} No issues found; the empty issue list was generated."
    exit 0
fi
echo ""

# Step 3: Fetch GitLab issue details
log "Step 3/5: Fetching GitLab issue details..."
python3 "$SCRIPT_DIR/fetch-gitlab-issue-details/implementation.py" \
    --input "$TEMP_DIR/01-issues.json" \
    --output "$TEMP_DIR/02-issue-details.json" \
    || error "Failed to fetch GitLab details"

log "Fetched details for $ISSUE_COUNT issues"
echo ""

# Step 4: Split notes by time
log "Step 4/5: Classifying notes by time..."
python3 "$SCRIPT_DIR/split-issue-notes-by-time/implementation.py" \
    --days $DAYS \
    --input "$TEMP_DIR/02-issue-details.json" \
    --output "$TEMP_DIR/03-classified-issues.json" \
    || error "Failed to classify notes"

log "Notes classified into current week and historical"
echo ""

# Step 5: Generate report
log "Step 5/5: Generating weekly report with LLM..."

# Check if API key is set (try both env var names)
if [ -z "$OPENROUTER_API_KEY" ] && [ -z "$ANTHROPIC_API_KEY" ]; then
    error "OPENROUTER_API_KEY environment variable not set. Get your API key at https://openrouter.ai/"
fi

# Build date argument
GENERATOR_ARGS=(
    --input "$TEMP_DIR/03-classified-issues.json"
    --output-dir "$OUTPUT_DIR"
)
if [ -n "$REPORT_DATE" ]; then
    GENERATOR_ARGS+=(--date "$REPORT_DATE")
fi

python3 "$SCRIPT_DIR/generate-tech-support-weekly-report/implementation.py" \
    "${GENERATOR_ARGS[@]}" \
    || error "Failed to generate report"

echo ""

# Cleanup temp directory
rm -rf "$TEMP_DIR"

# Summary
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Weekly Report Generation Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Report saved to: $OUTPUT_DIR"
echo ""
echo "Files generated:"
echo "  - weekly_issue_list_*.md   (Issue 明细列表)"
echo "  - weekly_report_table_*.md  (原始表格)"
echo "  - weekly_report_*.md         (完整周报)"
echo ""
echo "To view the report:"
echo "  ls -la $OUTPUT_DIR/weekly_report_*.md | tail -1"
echo ""
