---
name: daily-worklog-recorder
description: Use when 记录工时 / 记一下今天的工作 / 汇总今天做的事建 issue / 工时日报 / worklog —— 把当天的工作汇总成 GitLab（glab）项目的一条任务 issue，并用 /spend 记工时。含 glab CLI 404 规避、/spend 快捷指令响应坑、三处一致核验。
---

# Daily Worklog Recorder

把一天的工作汇总成 GitLab 项目的一条 issue + timelog 工时。产出三处一致的记录：**描述里的工时表**（人读）、**/spend timelog**（机器统计源）、**当日工时评论**（快照）。

## 目标项目配置

通过环境变量或运行时参数提供目标 GitLab 主机和项目，不要把主机、项目 ID 或项目名称写死在指令里。日常工作记录与产品研发 Issue 分开：工作日志项目由用户明确指定，不从当前工作目录、当前 Git 远端、关联研发 Issue/MR 或 `glab` 默认仓库推断。

**项目选择门禁**：每次创建或查重前先确定 `GITLAB_HOST` 和 `WORKLOG_PROJECT_ID`：用户必须明确提供；再用 `glab api --hostname "$GITLAB_HOST" "projects/<id>"` 核验项目。项目不匹配时停止，不创建 Issue、不写入 `/spend`。

执行时仍通过环境变量传入项目，避免命令中散落硬编码：

```bash
export GITLAB_HOST="<gitlab host>"
export WORKLOG_PROJECT_ID="<group/project 或数字 id>"
```

若目标项目有个人周报 issue 机制（周粒度、单独模板），注意区分：本 skill 记的是**单日工作项日志**；周报 issue 本身不要 /spend，防止与工作项 timelog 双计。

## 流程

### 1. 定日期、收工作项

- 「今天」= 用户话里的实际日期（用真实当前日期，别拿会话里最早出现的日期；跨午夜会话要向用户确认归属哪天）。
- 工作项来源按可信度排序：**用户口述 > 当前会话第一手 > 带日期的记忆条目**。记忆里的条目要核对该日期确实落在目标日。
- 来源不足就问用户，**不编造工作内容**。

### 2. 查重（防一天两条）

```
glab api --hostname "$GITLAB_HOST" "projects/<id>/issues?search=<日期 YYYY-MM-DD>&per_page=10&order_by=created_at&sort=desc"
```

先按日期查重，再按**工作功能/客户项目**判断归属：同一功能或同一连续工作项追加到原 Issue；不同功能、不同客户项目分别建 Issue，不要为了“同日一条”把无关工作合并。用户明确要求拆分时以用户要求为准。只有工时已由用户明确确认后，才更新对应 Issue 的工时表、追加 `/spend` 和发布该工作项的当日工时评论。

### 3. 选模板、建 issue

- 先读目标项目的 Issue 模板列表，按工作性质选择，并参考该项目既有同类 Issue 的标题前缀、标签、小节惯例，**不凭空发明格式**。
- 标题遵循目标项目现有格式，不凭空发明前缀。
- 描述按模板小节填：目的与内容（每项 2-4 行，写清产出和关联 MR/issue 号）/ 是否已完成 / 结果 / 工时表（`| # | 工作项 | 工时(h) |`）。工时未确认时可写「待确认」，但不调用 `/spend`，也不发布工时评论。
- **措辞中性化**：敏感来源（批评、事故）不点名不展开，只写做了什么。

### 4. 确认工时后再记工时（红线区）

- **确认门禁**：只有用户明确给出或确认了精确时长后，才可以更新描述中的工时数字、调用 `/spend` 和发布当日工时评论。未确认时，创建或补充工作记录后停止在「待确认」状态。
- **估算不等于确认**：用户要求“预估”时，只能给出保守建议并说明它是估算；必须等待用户明确确认记账时长（例如“按 2h 记录”）后，才能写入 GitLab。
- **工时数字不编造**：不得从任务复杂度、对话长度或历史记录推断工时；用户未提供或确认时，不得写入任何工时数字。
- 计时用 /spend 快捷指令 note：

```bash
glab api --hostname "$GITLAB_HOST" --method POST -f "body=/spend 1h30m 2026-10-13" "projects/<id>/issues/<iid>/notes"
```

- **最大的坑：纯快捷指令 note 的响应是 `commands_changes`，没有 note 对象**——看到 `{"commands_changes":{"spend_time":{...}},"summary":["Added …"]}` 就是**成功**，无 note id 属正常，**勿误判失败重试**（重试=双计）。
- 日期格式 `YYYY-MM-DD`，时长 `1h / 30m / 1h30m`。
- 记错冲销：`/spend -1h30m 2026-10-13`（负数同样走 note）。
- **`glab issue create` CLI 对部分项目会 404**，建单一律用 API：`glab api --hostname "$GITLAB_HOST" --method POST -f title=… -f description="$(cat /tmp/desc.md)" -f labels=… -f assignee_id=<uid> projects/<id>/issues`；uid 从本人名下既有 issue 的 `author.id` 反查，不要猜。
- 描述先写进 /tmp 文件再 `$(cat …)`，避免引号地狱；中文查询串必须 percent-encode，否则 400。

### 5. 确认后评论 + 核验收口

```bash
# 当日快照评论（正常 note，有 id）
glab api --hostname "$GITLAB_HOST" --method POST -f "body=**周X（YYYY-MM-DD）工时：Xh** —— <事项列表>" "projects/<id>/issues/<iid>/notes"
# 核验 timelog 总数 == 表格合计
glab api --hostname "$GITLAB_HOST" "projects/<id>/issues/<iid>" | python3 -c "import json,sys;print(json.load(sys.stdin)['time_stats']['human_total_time_spent'])"
```

确认后，描述工时表、`/spend` timelog 和当日工时评论三处数字必须一致才算完成。最后回报：issue 链接、timelog 合计、评论链接。工时未确认时，只回报工作记录 issue 链接与「待确认」状态。
