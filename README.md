# Codex Skills

Codex Skill 集合，按来源和维护关系独立组织，便于复用、审查和安装。

## 目录

### 个人维护

| Skill | 用途 |
|---|---|
| `ai-slop-cleaner` | 识别和清理 AI 生成内容中的冗余表达 |
| `atlas` | 控制 ChatGPT Atlas 浏览器 |
| `daily-worklog-recorder` | 把当天工作汇总成 GitLab issue 并用 /spend 记工时 |
| `okr-review-manager` | 汇总 OKR 进度并生成月度复盘草稿 |
| `onboard-new-user` | 设计新用户引导流程 |
| `review-software-design` | 评审软件设计和架构方案 |
| `teach` | 解释技术概念和代码实现 |
| `ticket-daily-summary` | 汇总支持门户当日工单更新（有人工回复的），确认后写入各工单绑定的 GitLab issue |
| `wechat-article-layout` | 优化微信公众号文章排版 |
| `weekly-report-generator` | 从工时和 Issue 数据生成技术支持周报 |

### Matt 工作流相关

以下 Skill 与 Matt 工作流相关，或依赖同一套工作流约定；不默认视为本仓库原创：

| Skill | 用途 |
|---|---|
| `ask-matt` | 按阶段推进复杂开发任务 |
| `grill-me` | 对方案进行追问和压力测试 |
| `grill-with-docs` | 结合文档进行方案校准 |
| `handoff` | 在任务或环境之间交接工作 |
| `implement` | 按已确认方案执行实现 |
| `improve-codebase-architecture` | 改进代码库架构和模块设计 |
| `to-questionnaire` | 将需求转化为澄清问题 |
| `to-spec` | 将需求整理为技术规格 |
| `to-tickets` | 将规格拆分为可执行任务 |
| `triage` | 分析问题并确定处理路径 |
| `wait-what` | 识别需求、代码或文档中的歧义 |
| `wayfinder` | 组织复杂任务的探索和推进路径 |

### 其他来源或改编

| Skill | 说明 |
|---|---|
| `superpower-dev-flow` | Superpowers 风格的开发流程 Skill，来源和许可以原仓库说明为准 |

Skill 的来源分类是维护信息，不代表对原作者、许可证或版权归属的法律判断。

## 安装

将需要的 Skill 目录复制到本地 Codex Skill 目录：

```bash
cp -R skills/<category>/<skill-name> ~/.codex/skills/
```

例如：

```bash
cp -R skills/personal/okr-review-manager ~/.codex/skills/
```

## 目录结构

```text
.
├── README.md
└── skills/
    ├── personal/<skill-name>/
    ├── matt-derived/<skill-name>/
    └── other/<skill-name>/
```

每个 Skill 保持独立，包含自己的触发条件、执行规则和必要资源。Skill 名称使用小写字母、数字和连字符。

## 公开仓库说明

本仓库为公开仓库，只提交通用的 Skill 指令、模板和示例。访问令牌、密码、数据库连接信息、客户隐私数据和未脱敏的内部配置不应提交到仓库。

需要访问内部系统的 Skill 应通过环境变量、用户本地配置或运行时参数获取凭据。发布前应检查内部 URL、个人路径、日志和示例数据，必要时替换为占位符。

## 维护规则

- 每个 Skill 单独维护，变更应保持范围清晰。
- 重要行为变化同步更新对应 `SKILL.md` 和 README 条目。
- 新增 Skill 前先确认它是可复用能力，而不是一次性任务记录。
- 发布前检查敏感信息和可执行示例。
