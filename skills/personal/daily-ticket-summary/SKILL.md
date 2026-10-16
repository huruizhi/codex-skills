---
name: daily-ticket-summary
description: Use when 获取今日/昨日工单更新、工单日报、工单汇总、把工单摘要总结写入 issue — 拉取极狐支持门户生产库当日有人工回复的工单，汇总成表格给用户确认后写入各工单绑定的 customer-success-teamwork issue（只汇总不@人）。端到端：kubectl 进生产 pod 查库 → 按口径筛选 → 汇总表格确认 → glab 发评论 → 复核新回复。需要 kubectl 集群访问权限与已认证的 glab (jihulab.com)。
---

# 工单日报（生产库 → 绑定 Issue）

固定目标：极狐支持门户生产环境，把某日（默认今天或昨天，**先和当前日期对齐**）有真实处理的工单汇总成日报，写入每个工单绑定的 GitLab issue。

## 硬性口径

1. **"有更新" = 当天有人工回复**：`TicketReply` 存在 `create_time` 落在窗口内且 `author_type ∈ ('agent','customer')` 的记录。仅有状态流转、系统自动消息（author_type=system 的超时提醒/自动关闭语）**不算**，只列入"口径外剔除"名单供透明。
2. **只汇总写入 issue，不 @ 任何人员**（2026-10-16 用户明确）：结尾不放 @ 行、不放"请登记工时"行。内部人员、SRE、管理员都不 @。
3. **汇总确认后才写入**：汇总完成后先输出**表格**（工单号/主题·公司/状态/负责人/绑定 issue/当日要点），**不得自动提交任何评论**；必须等用户明确确认后才执行写入。
4. **标题日期 = 数据归属日**：报昨日数据就写昨日日期，不用发送日。

## 第一步：生产库查询（kubectl exec，不用 stdin）

生产命名空间 `support-portal-13582-production`，pod 会频繁轮换，每次先重选：

```bash
kubectl get pod -n support-portal-13582-production | grep "support-portal-server" | grep Running | head -2
```

**禁止** `kubectl exec -i` + heredoc 喂 stdin（SPDY 丢帧 → InteractiveConsole 莫名 SyntaxError）。可靠模式 = 脚本 base64 后走 argv，pod 内 `shell -c` 一次性 exec。把下面模板存 `/tmp/podrun.sh`（改 POD 为当前 pod 名）：

```bash
#!/bin/bash
# usage: podrun.sh <local-script.py>
POD=support-portal-server-XXXX
NS=support-portal-13582-production
B64=$(base64 < "$1" | tr -d '\n')
for i in 1 2 3 4 5 6 7 8; do
  kubectl exec -n $NS $POD -c server -- sh -c "cd /code && python manage_pro.py shell -c 'import base64;exec(base64.b64decode(\"$B64\").decode())'"
  rc=$?
  if [ $rc -eq 0 ]; then exit 0; fi
  echo "--- attempt $i failed rc=$rc, retrying ---" >&2
  sleep 6
done
exit 1
```

查询脚本要点（全部踩过的坑，别省略）：

- 窗口：`timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)` 得当日零点（TIME_ZONE=Asia/Shanghai, USE_TZ=True）；昨日 = 当日零点 `- datetime.timedelta(days=1)`，区间用 `__gte=start, __lt=end`。
- **exec 作用域坑**：脚本里 `def` 函数体引用顶层 `import` 的名字会 NameError——把 `import re`、`from django.utils.html import strip_tags` 写进**函数体内**；模块级代码引用顶层导入没问题。
- 模型（`apps.support_ticket.models`）：`SupportTicket`（ticket_no/subject/company/status/assignee/support_primary_engineer/update_time，SoftModel 需 `is_deleted=False`）、`TicketReply`（author/author_type/visibility/body）、`TicketActivity`（actor/event_type，BaseModel 无 is_deleted）、`TicketGitLabIssueLink`（gitlab_project_id/gitlab_issue_iid/gitlab_issue_url）。
- 参与人统计剔除自动事件：`customer_reply_notification / assignment_notification / sla_warning / sla_breached / sla_reminder`，actor 为 None 的也算系统侧。
- 回复/描述正文 `strip_tags` + 压缩空白后截断（回复 400 字、描述 300 字）再输出，输出用 `|` 分隔行格式。
- 脚本末尾 `print('ALLDONE')`。**成功判据 = rc=0 且输出末行是 ALLDONE**；不要 grep 标记词（错误信息里也会出现该词），不要 `kubectl | tail` 管道（if 判断的是 tail 的退出码）。
- 输出里带：qualified 工单全量明细（===TICKET/REPLY/ACT/===END）、STATUS_ONLY 剔除名单、LINK 绑定关系、ACTORS 参与人。

第二次复查"有没有新回复"时直接重跑同一脚本，`diff` 两次输出即可。

## 第二步：汇总表格（停止点，等确认）

汇总输出为**一张表格**，同时作为待写评论的预览：

| 工单 | 主题 / 公司 | 状态 | 负责人 | Issue | 当日要点 |

- "当日要点"列写清客户诉求、我方动作、当前等待点（1-3 句，与将来评论正文一致；截断处的内容不要脑补）；
- 表格外补三样：口径外剔除名单（一句话）、内部参与人员（按事件数排序，区分工程师/客户侧，注明 SRE 介入）、**未来几天已约定的支持安排**（会议/升级窗口）；
- **输出表格后即停止本轮动作**，等待用户确认；用户未确认不得写入任何评论。

## 第三步：写入 issue（仅在用户明确确认后执行）

每单一个 markdown 文件（`/tmp/ticket_comments/<iid>.md`）：

```markdown
**工单日报 2026-10-15（10月15日）**

- 工单：SP-xxxxxxxx-xxxxx 主题（公司）
- 当前状态：等客户
- 当日进展：<事实，不推断；截断处的内容不要脑补>
- 当日处理：<工程师（回复 N 条/会议 N 场）+ SRE 协作等>

**注意：有明确时间的会议/升级窗口在此加粗。**（没有就整行省略）
```

批量发送（先发 1 条验证格式再批量）：

```bash
glab issue note <iid> -R jihulab.com/jihulab/customersuccess/customer-success-teamwork -m "$(cat /tmp/ticket_comments/<iid>.md)"
```

发完汇报 note 链接清单。**不含任何 @。**

### 修正误发

- 删评论：`glab api -X DELETE "projects/jihulab%2Fcustomersuccess%2Fcustomer-success-teamwork/issues/<iid>/notes/<nid>" --hostname jihulab.com`
- 改评论：同 URL `-X PUT --input body.json -H "Content-Type: application/json"`，body.json 内容 `{"body": "..."}`（python json.dumps 生成）。
- zsh 循环配对参数用 `${pair%%:*}` / `${pair##*:}`，**`set -- $pair` 不分词**。

## 备查

- 工程师 portal gitlab_user_id → jihulab username（如需反查他人：`glab api users/<id> --hostname jihulab.com`）：彭锐 15200=pengrui1、李发富 2129=ffli、唐小鸣 15194=xmtang、王凯旋 2757=wangkaixuan、张永宝 29853=zyb、雷程 14471=Andy.lei、陶郭宇 134=zookeeper、韩飞 6501=fred、陈仕员(SRE) 10=shreychen。
- **贺强强（qqhe@gitlab.cn）不是工程师**——他会回复工单/执行 SRE 操作，但不计入工程师名单。管理员（User id 1, gladmin）是共享运维账号。两者都不 @。
- 双库陷阱：测试 pod 里 `manage_pro.py` 连的也是生产库；本 skill 固定在生产命名空间 + `manage_pro.py`，若哪天要在测试环境演练，必须改用 `manage_test.py`。
