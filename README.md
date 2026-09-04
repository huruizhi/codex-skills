# Codex Skills

个人维护的 Codex Skill 集合，按目录独立组织，便于复用、审查和安装。

## Skills

| Skill | 用途 |
|---|---|
| `ai-slop-cleaner` | 识别和清理 AI 生成内容中的冗余表达 |
| `ask-matt` | 按阶段推进复杂开发任务 |
| `atlas` | 控制 ChatGPT Atlas 浏览器 |
| `grill-me` | 对方案进行追问和压力测试 |
| `grill-with-docs` | 结合文档进行方案校准 |
| `handoff` | 在任务或环境之间交接工作 |
| `implement` | 按已确认方案执行实现 |
| `improve-codebase-architecture` | 改进代码库架构和模块设计 |
| `okr-review-manager` | 汇总 OKR 进度并生成月度复盘草稿 |
| `onboard-new-user` | 设计新用户引导流程 |
| `review-software-design` | 评审软件设计和架构方案 |
| `superpower-dev-flow` | 推进结构化开发流程 |
| `teach` | 解释技术概念和代码实现 |
| `to-questionnaire` | 将需求转化为澄清问题 |
| `to-spec` | 将需求整理为技术规格 |
| `to-tickets` | 将规格拆分为可执行任务 |
| `triage` | 分析问题并确定处理路径 |
| `wait-what` | 识别需求、代码或文档中的歧义 |
| `wayfinder` | 组织复杂任务的探索和推进路径 |
| `wechat-article-layout` | 优化微信公众号文章排版 |
| `weekly-report-generator` | 从工时和 Issue 数据生成技术支持周报 |

## 安装

将需要的 Skill 目录复制到本地 Codex Skill 目录：

```bash
cp -R skills/<skill-name> ~/.codex/skills/
```

例如：

```bash
cp -R skills/okr-review-manager ~/.codex/skills/
```

## 目录结构

```text
.
├── README.md
└── skills/
    └── <skill-name>/
        ├── SKILL.md
        ├── agents/openai.yaml
        ├── references/      # 可选
        └── scripts/         # 可选
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
