---
name: okr-review-manager
description: Generate and review monthly OKR progress summaries for the technical support team from GitLab OKR data and related project work. Use when collecting personal KR updates, preparing department O/KR reviews, or checking OKR status before a confirmed GitLab update.
---

# OKR Review Manager

Use this skill for the technical support team's OKR monthly review workflow. Keep the workflow lightweight: collect evidence, ask for missing management context, generate a draft, grill the draft with the user, and only then update GitLab when explicitly confirmed.

## Scope

- Department and personal OKR project URLs are organization-specific; obtain them from the user or the current workspace configuration.
- Related progress sources may include configured support projects when the user asks for department-level aggregation.
- Use `glab` for GitLab reads and writes. Do not modify issue descriptions, templates, labels, milestones, parent relationships, or comments unless the user explicitly requests that operation.

## Workflow

### 1. Establish the review period

Interpret “this month”, “last month”, or a named month using the user's timezone and state the exact period in the draft. Do not silently mix monthly work with historical context.

### 2. Collect evidence

For each relevant personal O/KR, inspect the issue or work item and its review comments. Extract only evidence-backed information:

- current progress;
- health status;
- completed work during the review period;
- blockers or needed resources;
- next-month actions;
- whether the engineer has submitted a review.

For a department review, also inspect the department O/KR and requested supporting projects, then add the manager's own work separately so it is not incorrectly attributed to an engineer KR.

### 3. Identify gaps and ask questions

Before writing a department review, list missing or uncertain items. Ask concise questions about:

- the manager's own work;
- whether a result is formal or still exploratory;
- evidence behind percentages or customer-impact claims;
- blockers and resource requests;
- the intended pace of O1, O2, and O3.

Do not fill uncertain facts by inference. A review can state that data or samples are still being collected.

### 4. Generate the draft

For department reviews, use this structure:

```markdown
## YYYY-MM 月度复盘（部门级）

### 目标与 KR 进展总结
| 关键结果 (KR) | 当前进度 | 健康状态 | 本月完成关键事项 | 阻碍 / 所需资源 |
|---|---|---|---|---|
| **O1: xxx** | - | - | 1. xxx<br>2. xxx | - |
| KR1: xxx | xx% | 进度正常 / 有风险 / 阻塞 | 1. xxx<br>2. xxx | 1. xxx |

### 下月关键动作
| 关键动作 | Owner | 预计完成时间 |
|---|---|---|
| xxx | @owner | YYYY-MM-DD |
```

For personal reviews, preserve the engineer's own facts and organize them under O/KR rather than rewriting their work as department achievements.

Use `<br>` for multiple items in a Markdown table cell. Keep progress wording conservative: “阶段性完成”“形成初步机制”“进入试运行准备”“已沉淀样例”“仍需补充数据或客户样本”.

### 5. Grill and calibrate

Before any GitLab mutation, review the draft with the user. Check:

- every stated result has a source;
- percentages have a clear basis or are marked as estimates;
- O, KR, Task, labels, checklist states, and parent relationships are not being treated as interchangeable;
- the draft separates engineer work, manager work, and project evidence;
- blockers and resource requests are concrete;
- customer, AI, DAP, satisfaction, coverage, or efficiency claims are not overstated;
- the wording is suitable for leadership review.

If the user has not confirmed the content, output the draft and questions only.

### 6. Update GitLab after confirmation

After explicit confirmation, use `glab` to update the existing monthly review comment or the requested O/KR work item. Prefer updating an existing review record over creating a duplicate. Report what was updated and provide the direct link.

## Review rules

- Separate the following layers: company KR, department O, department KR, personal O, and personal KR/Task.
- A department O progress value is a management judgment based on KR evidence; it is not automatically the arithmetic average of KR percentages.
- “进度正常” is appropriate only when the evidence supports the planned pace.
- Keep KA customer support, DAP support, Atlas AI work, ticketing, documentation, and process work under the correct O/KR; do not count the same activity twice.
- Treat GitLab labels, descriptions, checklists, comments, and parent links as separate signals. Surface inconsistencies instead of silently resolving them.
- When the user asks for a DingTalk message, produce a concise copyable list without changing the review record.

## Default outputs

Unless the user asks for a different format, provide:

1. personal review completion and gap list;
2. personal KR progress summary;
3. department O/KR review draft when requested;
4. concise questions for missing manager input;
5. source and uncertainty notes for leadership review.

Do not automatically create goals, milestones, labels, board changes, or scheduled automations as part of an OKR review.
