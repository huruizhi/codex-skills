---
name: daily-worklog-recorder
description: Use when 记录工时 / 记一下今天的工作 / 汇总今天做的事建 issue / 工时日报 / worklog —— 把当天的工作汇总成 GitLab（glab）项目的一条任务 issue，并用 /spend 记工时。含 glab CLI 404 规避、/spend 快捷指令响应坑、三处一致核验。
---

# Daily Worklog Recorder

把一天的工作汇总成 GitLab 项目的一条 issue + timelog 工时。产出三处一致的记录：**描述里的工时表**（人读）、**/spend timelog**（机器统计源）、**当日工时评论**（快照）。

## 目标项目配置

通过环境变量或运行时参数提供，不要把项目 ID 写死在指令里：

```bash
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
glab api "projects/<id>/issues?search=<日期 YYYY-MM-DD>&per_page=10&order_by=created_at&sort=desc"
```

同日已有日志 issue → **追加**（描述表格加行 + 追加 /spend + 新评论），不建新单。

### 3. 选模板、建 issue

- 先读项目 `.gitlab/issue_templates/` 下的模板列表，按工作性质选（内部工作 → 内部服务/日常任务类模板；客户工单 → 工单任务类模板），并参考项目里既有同类 issue 的标题前缀、标签、小节惯例，**不凭空发明格式**。
- 标题建议：`<模板前缀>-<内容概括>（YYYY-MM-DD）`。
- 描述按模板小节填：目的与内容（每项 2-4 行，写清产出和关联 MR/issue 号）/ 是否已完成 / 结果 / 工时表（`| # | 工作项 | 工时(h) |`）。
- **措辞中性化**：敏感来源（批评、事故）不点名不展开，只写做了什么。

### 4. 记工时（红线区）

- **工时数字不编造**：用户没给就先留「待填」，明确委托估算时按实际工作量保守取值并在回复里说清是估算。
- 计时用 /spend 快捷指令 note：

```bash
glab api --method POST -f "body=/spend 1h30m 2026-10-13" "projects/<id>/issues/<iid>/notes"
```

- **最大的坑：纯快捷指令 note 的响应是 `commands_changes`，没有 note 对象**——看到 `{"commands_changes":{"spend_time":{...}},"summary":["Added …"]}` 就是**成功**，无 note id 属正常，**勿误判失败重试**（重试=双计）。
- 日期格式 `YYYY-MM-DD`，时长 `1h / 30m / 1h30m`。
- 记错冲销：`/spend -1h30m 2026-10-13`（负数同样走 note）。
- **`glab issue create` CLI 对部分项目会 404**，建单一律用 API：`glab api --method POST -f title=… -f description="$(cat /tmp/desc.md)" -f labels=… -f assignee_id=<uid> projects/<id>/issues`；uid 从本人名下既有 issue 的 `author.id` 反查，不要猜。
- 描述先写进 /tmp 文件再 `$(cat …)`，避免引号地狱；中文查询串必须 percent-encode，否则 400。

### 5. 评论 + 核验收口

```bash
# 当日快照评论（正常 note，有 id）
glab api --method POST -f "body=**周X（YYYY-MM-DD）工时：Xh** —— <事项列表>" "projects/<id>/issues/<iid>/notes"
# 核验 timelog 总数 == 表格合计
glab api "projects/<id>/issues/<iid>" | python3 -c "import json,sys;print(json.load(sys.stdin)['time_stats']['human_total_time_spent'])"
```

三处数字必须一致才算完成。最后回报：issue 链接、timelog 合计、评论链接。
