---
name: generate-tech-support-weekly-report
description: Use when classified current-week and historical GitLab Issue comments must be converted into a Chinese technical-support narrative report through OpenRouter.
---

# Generate Technical-Support Weekly Report

Read the classified JSON produced by `split-issue-notes-by-time` and generate the existing table and narrative Markdown files.

Set `OPENROUTER_API_KEY`; do not store API keys in the Skill.

```bash
python3 implementation.py \
  --input /tmp/weekly-report/03-classified-issues.json \
  --output-dir ~/Documents/Obsidian/05-Work/weekly \
  --date 2026-07-20
```

This stage is optional for Issue-list generation. Use `generate-issue-list.sh` when only the deterministic Issue list is required.
