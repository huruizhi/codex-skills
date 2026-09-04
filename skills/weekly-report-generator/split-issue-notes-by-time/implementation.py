#!/usr/bin/env python3
"""
Split Issue Notes by Time
Classifies issue notes into current week and historical categories.
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from typing import List, Dict, Any


def parse_timestamp(timestamp_str: str) -> datetime:
    """
    Parse ISO 8601 timestamp with timezone.

    Args:
        timestamp_str: ISO 8601 timestamp string

    Returns:
        datetime object with timezone
    """
    try:
        # Parse ISO 8601 format (handles timezone offsets like +08:00)
        return datetime.fromisoformat(timestamp_str)
    except (ValueError, TypeError):
        return None


def classify_notes(notes: List[Dict[str, str]], days_threshold: int = 7) -> Dict[str, List[str]]:
    """
    Classify notes into current and historical based on timestamp.

    Args:
        notes: List of note objects with 'body' and 'createdAt'
        days_threshold: Days to consider as "current" (default: 7)

    Returns:
        Dictionary with '本周工作' and '历史回顾' lists
    """
    now = datetime.now(timezone.utc)
    threshold_ms = days_threshold * 24 * 60 * 60 * 1000

    current = []
    historical = []

    for note in notes:
        body = note.get('body', '').strip()
        created_at = note.get('createdAt')

        if not body:
            continue

        # Parse timestamp
        timestamp = parse_timestamp(created_at)
        if timestamp is None:
            # If timestamp is invalid, put in historical
            historical.append(body)
            continue

        # Convert to UTC if not already
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        # Calculate time difference
        time_diff_ms = (now - timestamp).total_seconds() * 1000

        if time_diff_ms <= threshold_ms:
            current.append(body)
        else:
            historical.append(body)

    return {
        '本周工作': current,
        '历史回顾': historical
    }


def process_issues(issues: List[Dict[str, Any]], days_threshold: int = 7) -> Dict[str, Any]:
    """
    Process multiple issues and classify their notes.

    Args:
        issues: List of issue objects with notes
        days_threshold: Days to consider as "current"

    Returns:
        Dictionary with classified items and summary
    """
    items = []
    total_current_notes = 0
    total_historical_notes = 0

    for issue in issues:
        title = issue.get('title', '无标题')
        iid = issue.get('iid', '')
        web_url = issue.get('web_url', '')
        notes = issue.get('notes', [])

        classified = classify_notes(notes, days_threshold)

        item = {
            'title': title,
            'iid': iid,
            'web_url': web_url,
            **classified
        }

        items.append(item)
        total_current_notes += len(classified['本周工作'])
        total_historical_notes += len(classified['历史回顾'])

    return {
        'items': items,
        'summary': {
            'total_issues': len(items),
            'total_current_notes': total_current_notes,
            'total_historical_notes': total_historical_notes
        }
    }


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Split issue notes into current week and historical'
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Days to consider as "current" (default: 7)'
    )
    parser.add_argument(
        '--input',
        type=str,
        help='Input JSON file (reads from stdin if not provided)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output JSON file (writes to stdout if not provided)'
    )

    args = parser.parse_args()

    # Read input
    if args.input:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                issues = json.load(f)
        except FileNotFoundError:
            print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            issues = json.load(sys.stdin)
        except json.JSONDecodeError:
            print("Error: Invalid JSON from stdin", file=sys.stderr)
            sys.exit(1)

    if not isinstance(issues, list):
        print("Error: Input must be a JSON array of issues", file=sys.stderr)
        sys.exit(1)

    # Process issues
    result = process_issues(issues, args.days)

    # Print summary to stderr
    summary = result['summary']
    print(f"Processed {summary['total_issues']} issues:", file=sys.stderr)
    print(f"  - 本周工作: {summary['total_current_notes']} notes", file=sys.stderr)
    print(f"  - 历史回顾: {summary['total_historical_notes']} notes", file=sys.stderr)

    # Output results
    output = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Saved classified data to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
