#!/usr/bin/env python3
"""
Fetch GitLab Issue Details
Retrieves issue notes/comments using GitLab GraphQL API.
"""

import argparse
import json
import os
import sys
import time
from typing import List, Dict, Any
from urllib.parse import unquote, urlparse
import requests


# GitLab configuration
GITLAB_CONFIG = {
    'graphql_endpoint': os.getenv('GITLAB_GRAPHQL_ENDPOINT', 'https://jihulab.com/api/graphql'),
    'project_path': os.getenv(
        'GITLAB_PROJECT_PATH',
        'jihulab/customersuccess/customer-success-teamwork'
    ),
}

# GraphQL query (no leading newline)
GRAPHQL_QUERY = """query IssueNotes($fullPath: ID!, $iid: String!) {
  project(fullPath: $fullPath) {
    issue(iid: $iid) {
      title
      notes(first: 100) {
        pageInfo {
          hasNextPage
          endCursor
        }
        nodes {
          body
          createdAt
        }
      }
    }
  }
}"""


def fetch_issue_notes(iid: str, project_path: str, token: str) -> Dict[str, Any]:
    """
    Fetch issue notes using GraphQL API.

    Args:
        iid: Issue IID
        token: Personal access token (uses default if None)

    Returns:
        Dictionary with issue title and notes
    """
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    variables = {
        'fullPath': project_path,
        'iid': str(iid)
    }

    payload = {
        'query': GRAPHQL_QUERY,
        'variables': variables
    }

    try:
        response = requests.post(
            GITLAB_CONFIG['graphql_endpoint'],
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()

        data = response.json()

        # Check for errors
        if 'errors' in data:
            error_msg = data['errors'][0].get('message', 'Unknown error')
            print(f"Error fetching issue {iid}: {error_msg}", file=sys.stderr)
            return None

        # Extract issue data
        issue_data = data.get('data', {}).get('project', {}).get('issue')

        if issue_data is None:
            print(f"Warning: Issue {iid} not found or no access", file=sys.stderr)
            return None

        return {
            'iid': iid,
            'title': issue_data.get('title', ''),
            'notes': issue_data.get('notes', {}).get('nodes', [])
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching issue {iid}: {e}", file=sys.stderr)
        return None


def extract_iid_from_url(url: str) -> str:
    """Extract issue IID from GitLab URL."""
    if not url:
        return None
    parts = url.rstrip('/').split('/')
    if parts and parts[-1].isdigit():
        return parts[-1]
    return None


def extract_project_path(url: str) -> str:
    """Extract the GitLab project full path from an issue URL."""
    if not url:
        return None
    parts = [part for part in unquote(urlparse(url).path).split('/') if part]
    marker_indexes = [
        index for index, part in enumerate(parts)
        if part in {'issues', 'work_items'}
    ]
    if not marker_indexes:
        return None
    marker_index = marker_indexes[-1]
    project_parts = parts[:marker_index]
    if project_parts and project_parts[-1] == '-':
        project_parts.pop()
    return '/'.join(project_parts) or None


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Fetch GitLab issue details using GraphQL API'
    )
    parser.add_argument(
        '--input',
        type=str,
        help='Input JSON file with issue URLs (reads from stdin if not provided)'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='Output JSON file (writes to stdout if not provided)'
    )
    parser.add_argument(
        '--token',
        type=str,
        help='GitLab personal access token'
    )
    parser.add_argument(
        '--delay',
        type=float,
        default=0.5,
        help='Delay between API requests in seconds (default: 0.5)'
    )

    args = parser.parse_args()

    token = args.token or os.getenv('GITLAB_TOKEN')
    if not token:
        print("Error: GitLab token not provided; set GITLAB_TOKEN or use --token", file=sys.stderr)
        sys.exit(1)

    # Read input
    if args.input:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            input_data = json.load(sys.stdin)
        except json.JSONDecodeError:
            print("Error: Invalid JSON from stdin", file=sys.stderr)
            sys.exit(1)

    if isinstance(input_data, dict):
        issues = input_data.get('items', [])
    else:
        issues = input_data

    if not isinstance(issues, list):
        print("Error: Input must be an issue array or an object containing items", file=sys.stderr)
        sys.exit(1)

    # The weekly query has one row per engineer and issue. Fetch each issue once.
    unique_issues = []
    seen = set()
    for issue in issues:
        iid = issue.get('iid') or extract_iid_from_url(issue.get('web_url'))
        project_path = extract_project_path(issue.get('web_url')) or GITLAB_CONFIG['project_path']
        key = (project_path, str(iid or ''))
        if iid and key not in seen:
            seen.add(key)
            unique_issues.append((issue, str(iid), project_path))

    # Fetch details for each issue
    results = []
    total = len(unique_issues)

    for i, (issue, iid, project_path) in enumerate(unique_issues, 1):

        print(f"Fetching issue {i}/{total}: {iid}...", file=sys.stderr)

        issue_details = fetch_issue_notes(iid, project_path, token)

        if issue_details:
            # Add web_url if available in input
            if 'web_url' in issue:
                issue_details['web_url'] = issue['web_url']
            results.append(issue_details)

        # Add delay to avoid rate limiting
        if i < total:
            time.sleep(args.delay)

    # Output results
    output = json.dumps(results, ensure_ascii=False, indent=2)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"Saved {len(results)} issue details to {args.output}", file=sys.stderr)
    else:
        print(output)


if __name__ == '__main__':
    main()
