---
name: fetch-gitlab-issue-details
description: Use when technical-support weekly-report data contains GitLab Issue URLs and the corresponding comments must be fetched through the GitLab GraphQL API.
---

# Fetch GitLab Issue Details

Read either an Issue array or the `items` object produced by `query-tech-support-issues`. Deduplicate the Issue/engineer rows before calling GitLab.

Set `GITLAB_TOKEN` or pass `--token`. Optionally set `GITLAB_GRAPHQL_ENDPOINT` and `GITLAB_PROJECT_PATH`. Never store access tokens in this Skill.

```bash
python3 implementation.py \
  --input /tmp/weekly-report/01-issues.json \
  --output /tmp/weekly-report/02-issue-details.json
```

Derive the project path from each Issue URL when possible. Use the configured project path only as a fallback.
