---
name: split-issue-notes-by-time
description: Use when GitLab Issue comments must be separated into recent work and historical context before generating a technical-support narrative report.
---

# Split Issue Notes by Time

Classify each comment by `createdAt` into `本周工作` or `历史回顾`.

```bash
python3 implementation.py \
  --days 7 \
  --input /tmp/weekly-report/02-issue-details.json \
  --output /tmp/weekly-report/03-classified-issues.json
```

This rolling comment window is separate from the natural-week timelog range used by the Markdown Issue list.
