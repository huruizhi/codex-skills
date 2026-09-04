---
name: weekly-report-generator
description: Use when generating weekly technical-support Issue lists or narrative reports from MySQL timelogs and GitLab comments, including engineer, customer, KA status, title, URL, and weekly time spent.
---

# Weekly Report Generator

Generate a deterministic Markdown Issue list first, then optionally fetch GitLab comments and generate the narrative report.

## Configure

Set database credentials through environment variables. Never store credentials in this Skill.

```bash
export WEEKLY_REPORT_DB_HOST="..."
export WEEKLY_REPORT_DB_PORT="3306"
export WEEKLY_REPORT_DB_NAME="portal"
export WEEKLY_REPORT_DB_USER="..."
export WEEKLY_REPORT_DB_PASSWORD="..."
export GITLAB_TOKEN="..." # Required only when fetching comments
```

Install runtime dependencies:

```bash
python3 -m pip install mysql-connector-python requests openai
```

## Generate the Issue list

Run the standalone Issue-list command. It does not require a GitLab token or an LLM key.

```bash
~/.codex/skills/weekly-report-generator/generate-issue-list.sh \
  --output ~/Documents/Obsidian/05-Work/weekly
```

Default to `~/Documents/Obsidian/05-Work/weekly`. Override it with `--output` or `WEEKLY_REPORT_OUTPUT_DIR` when needed.

Use `--date YYYY-MM-DD` to anchor the calculation. Always select the previous natural week in `Asia/Shanghai`, from Monday 00:00 inclusive to the next Monday 00:00 exclusive.

Write `weekly_issue_list_YYYYMMDD_YYYYMMDD.md` immediately after the database query. Do not require GitLab comments or an LLM to create this file.

## Issue-list contract

- Include only these engineers: 雷程、李发富、陶郭宇、韩飞、彭锐、王凯旋、张永宝、胡睿智。
- Include every Issue type; do not filter `Task_type`.
- Include Issue title/link, customer, handling engineer, KA status, and weekly hours.
- Aggregate timelogs by Issue and engineer. Keep separate rows when multiple engineers log time on the same Issue.
- Group Markdown by engineer, then by KA, non-KA, internal task, and unlinked customer.
- Map `support_customer_type = ka` to `是` and other known values to `否`.
- Map `Customer::内部服务`, `Inner`, and `DailyTasks` to `内部任务`; do not require customer mapping for them.
- Use `客户未关联` only for customer work whose customer master-data association is unavailable.

## Run the full report

Run `prepare-data.sh` to generate the Issue list plus classified GitLab comments. Run `run-full-pipeline.sh` to generate the Issue list and the existing narrative report. Set `GITLAB_TOKEN` when fetching comments and `OPENROUTER_API_KEY` for narrative generation.

Use the child skills only when working on an individual stage:

- `query-tech-support-issues`: produce structured weekly Issue/timelog JSON.
- `render-weekly-issue-list`: produce deterministic Markdown.
- `fetch-gitlab-issue-details`: fetch GitLab comments.
- `split-issue-notes-by-time`: separate recent and historical comments.
- `generate-tech-support-weekly-report`: generate the narrative report.
