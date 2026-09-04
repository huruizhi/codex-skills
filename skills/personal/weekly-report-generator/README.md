# 技术支持周报生成器

该个人 Skill 从 MySQL 工时记录生成上周技术支持 Issue Markdown 列表，并可继续获取 GitLab 评论、生成完整周报。

## Issue 列表

默认统计 Asia/Shanghai 时区的上一个自然周，不过滤 Issue 类型。统计人员为：雷程、李发富、陶郭宇、韩飞、彭锐、王凯旋、张永宝、胡睿智。

输出字段：Issue title/URL、客户名称、处理工程师、客户分类、本周工时。内部工作显示“内部任务”，缺少客户主数据关联的客户工作显示“客户未关联”。文件名为：

```text
weekly_issue_list_YYYYMMDD_YYYYMMDD.md
```

## 配置与运行

```bash
export WEEKLY_REPORT_DB_HOST="..."
export WEEKLY_REPORT_DB_PORT="3306"
export WEEKLY_REPORT_DB_NAME="portal"
export WEEKLY_REPORT_DB_USER="..."
export WEEKLY_REPORT_DB_PASSWORD="..."
export GITLAB_TOKEN="..."

~/.codex/skills/weekly-report-generator/generate-issue-list.sh \
  --output ~/Documents/Obsidian/05-Work/weekly
```

该命令只查询数据库并生成 Issue 列表，不依赖 GitLab 评论或 LLM。包含评论的数据准备使用 `prepare-data.sh`，完整周报使用 `run-full-pipeline.sh`。
