---
name: render-weekly-issue-list
description: Use when structured technical-support issue and timelog data must be rendered as a deterministic weekly Markdown issue list grouped by engineer and KA status.
---

# Render Weekly Issue List

Read the JSON produced by `query-tech-support-issues` and render a Markdown list with Issue title/link, customer, engineer, KA status, and weekly hours.

```bash
python3 implementation.py \
  --input /tmp/weekly-report/01-issues.json \
  --output-dir ~/Documents/Obsidian/05-Work/weekly
```

Keep one row per engineer and Issue. Sum duplicate rows for the same engineer and Issue. Render internal work as `内部任务` and missing customer-master associations as `客户未关联`.
