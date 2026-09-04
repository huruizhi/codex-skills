---
name: query-tech-support-issues
description: Use when a weekly technical-support Issue list needs structured MySQL timelog data for a natural-week date range, including customer, engineer, KA status, title, URL, and time spent.
---

# Query Technical-Support Issues

Query the previous natural week in `Asia/Shanghai` and return a JSON object containing `period`, the eight-engineer roster, and `items`.

```bash
python3 implementation.py --output /tmp/weekly-report/01-issues.json
python3 implementation.py --date 2026-07-20 --output /tmp/weekly-report/01-issues.json
python3 implementation.py --start-date 2026-07-13 --end-date 2026-07-20
```

Treat `--end-date` as exclusive. Aggregate `timeSpent` by Issue and engineer. Do not filter `Task_type`.

Require `WEEKLY_REPORT_DB_HOST`, `WEEKLY_REPORT_DB_USER`, and `WEEKLY_REPORT_DB_PASSWORD`. Accept `WEEKLY_REPORT_DB_PORT` and `WEEKLY_REPORT_DB_NAME` as optional configuration.

Return `内部任务` for internal-service, cross-department, and daily-task Issues without requiring customer mapping. Return `客户未关联` for customer work that cannot be associated with customer master data.
