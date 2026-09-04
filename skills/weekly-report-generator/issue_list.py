#!/usr/bin/env python3
"""Pure helpers for querying and rendering the weekly issue list."""

from collections import OrderedDict
from datetime import date, timedelta
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


TECH_SUPPORT_ENGINEERS = (
    "雷程",
    "李发富",
    "陶郭宇",
    "韩飞",
    "彭锐",
    "王凯旋",
    "张永宝",
    "胡睿智",
)

KA_SECTION_NAMES = OrderedDict(
    (
        ("是", "KA"),
        ("否", "非 KA"),
        ("内部任务", "内部任务"),
        ("客户未关联", "客户未关联"),
    )
)


def previous_natural_week(anchor_date: date) -> Tuple[date, date]:
    """Return the previous Monday-to-Monday half-open date range."""
    current_monday = anchor_date - timedelta(days=anchor_date.weekday())
    return current_monday - timedelta(days=7), current_monday


def build_issue_query(has_ka_field: bool) -> Tuple[str, Tuple[str, ...]]:
    """Build the aggregate timelog query and its engineer parameters."""
    placeholders = ", ".join(["%s"] * len(TECH_SUPPORT_ENGINEERS))
    if has_ka_field:
        ka_select = """
        CASE
            WHEN b.Customer = 'Customer::内部服务'
              OR b.Task_type IN ('Inner', 'DailyTasks') THEN '内部任务'
            WHEN oe.support_customer_type = 'ka' THEN '是'
            WHEN oe.organization_id IS NULL THEN '客户未关联'
            ELSE '否'
        END AS is_ka"""
        ka_join = """
    LEFT JOIN gitlab_app_organizationextension AS oe
        ON b.Customer_id_id = oe.organization_id"""
        ka_group = ", oe.support_customer_type, oe.organization_id"
    else:
        ka_select = """
        CASE
            WHEN b.Customer = 'Customer::内部服务'
              OR b.Task_type IN ('Inner', 'DailyTasks') THEN '内部任务'
            ELSE '客户未关联'
        END AS is_ka"""
        ka_join = ""
        ka_group = ""

    query = f"""
    SELECT
        b.id AS issue_id,
        b.web_url,
        b.title,
        CASE
            WHEN b.Customer = 'Customer::内部服务'
              OR b.Task_type IN ('Inner', 'DailyTasks') THEN '内部任务'
            ELSE COALESCE(NULLIF(b.Customer, ''), '未标注客户')
        END AS customer,
        a.username AS engineer,
        {ka_select},
        SUM(a.timeSpent) AS time_spent_seconds
    FROM etl_timelogs AS a
    INNER JOIN etl_support_issues AS b
        ON a.issue_id_id = b.id
    {ka_join}
    WHERE
        a.spentAt >= %s
        AND a.spentAt < %s
        AND a.username IN ({placeholders})
    GROUP BY
        b.id, b.web_url, b.title, b.Customer, b.Task_type, a.username{ka_group}
    ORDER BY
        a.username, is_ka DESC, b.title
    """
    return query, TECH_SUPPORT_ENGINEERS


def normalize_ka(value: Any) -> str:
    if value is True or value == 1:
        return "是"
    if value is False or value == 0:
        return "否"
    normalized = str(value or "").strip().lower()
    if normalized in {"是", "ka", "yes", "true"}:
        return "是"
    if normalized in {"否", "paid", "trial_or_unknown", "no", "false"}:
        return "否"
    if normalized in {"内部任务", "内部服务", "internal", "internal_task"}:
        return "内部任务"
    return "客户未关联"


def escape_markdown_text(value: Any) -> str:
    text = " ".join(str(value or "").splitlines()).strip()
    return text.replace("\\", "\\\\").replace("|", "\\|").replace("]", "\\]")


def format_hours(seconds: Any) -> str:
    try:
        value = max(0, int(seconds or 0))
    except (TypeError, ValueError):
        value = 0
    return f"{value / 3600:.2f} 小时"


def _aggregate_items(items: Iterable[Mapping[str, Any]]) -> List[Dict[str, Any]]:
    aggregated: Dict[Tuple[str, str], Dict[str, Any]] = OrderedDict()
    for raw in items:
        engineer = str(raw.get("engineer") or raw.get("username") or "").strip()
        if not engineer:
            continue
        issue_key = str(
            raw.get("issue_id")
            or raw.get("id")
            or raw.get("web_url")
            or raw.get("title")
            or "无标识 Issue"
        )
        key = (engineer, issue_key)
        if key not in aggregated:
            aggregated[key] = {
                "issue_id": raw.get("issue_id") or raw.get("id"),
                "title": raw.get("title") or "无标题",
                "web_url": raw.get("web_url") or "",
                "customer": raw.get("customer") or raw.get("Customer") or "未标注客户",
                "engineer": engineer,
                "is_ka": normalize_ka(raw.get("is_ka")),
                "time_spent_seconds": 0,
            }
        try:
            aggregated[key]["time_spent_seconds"] += int(raw.get("time_spent_seconds") or 0)
        except (TypeError, ValueError):
            pass
    return list(aggregated.values())


def _engineer_order(payload: Mapping[str, Any], items: Sequence[Mapping[str, Any]]) -> List[str]:
    preferred = payload.get("engineers") or TECH_SUPPORT_ENGINEERS
    active = {str(item.get("engineer") or "") for item in items}
    ordered = [name for name in preferred if name in active]
    ordered.extend(sorted(active.difference(ordered)))
    return ordered


def _issue_link(item: Mapping[str, Any]) -> str:
    title = escape_markdown_text(item.get("title") or "无标题")
    url = str(item.get("web_url") or "").strip().replace(">", "%3E")
    return f"[{title}](<{url}>)" if url else title


def render_issue_list_markdown(payload: Mapping[str, Any]) -> str:
    """Render an issue payload as deterministic Markdown."""
    period = payload.get("period") or {}
    start_text = str(period.get("start") or "未知")
    end_exclusive_text = str(period.get("end") or "未知")
    try:
        end_inclusive_text = (date.fromisoformat(end_exclusive_text) - timedelta(days=1)).isoformat()
    except ValueError:
        end_inclusive_text = end_exclusive_text

    items = _aggregate_items(payload.get("items") or [])
    unique_issues = {
        str(item.get("issue_id") or item.get("web_url") or item.get("title"))
        for item in items
    }
    customers = {
        str(item.get("customer"))
        for item in items
        if item.get("customer") not in {None, "", "未标注客户", "内部任务"}
    }
    total_seconds = sum(int(item.get("time_spent_seconds") or 0) for item in items)

    lines = [
        f"# 技术支持 Issue 列表（{start_text} 至 {end_inclusive_text}）",
        "",
        "> 统计口径：时间范围内有工时记录的 Issue；不按 Issue 类型过滤；同一工程师在同一 Issue 的工时合并；内部工作不参与 KA 判断。",
        "",
        f"- Issue 数：{len(unique_issues)}",
        f"- 客户数：{len(customers)}",
        f"- 处理工程师数：{len(_engineer_order(payload, items))}",
        f"- 总工时：{format_hours(total_seconds)}",
        "",
    ]

    if not items:
        lines.extend(["本周期没有符合条件的 Issue。", ""])
        return "\n".join(lines)

    for engineer in _engineer_order(payload, items):
        engineer_items = [item for item in items if item["engineer"] == engineer]
        lines.extend([f"## {escape_markdown_text(engineer)}", ""])
        for ka_value, section_name in KA_SECTION_NAMES.items():
            section_items = [item for item in engineer_items if item["is_ka"] == ka_value]
            if not section_items:
                continue
            lines.extend(
                [
                    f"### {section_name}",
                    "",
                    "| Issue | 客户名称 | 处理工程师 | 客户分类 | 本周工时 |",
                    "|---|---|---|---|---:|",
                ]
            )
            for item in sorted(
                section_items,
                key=lambda row: (str(row.get("customer") or ""), str(row.get("title") or "")),
            ):
                lines.append(
                    "| {issue} | {customer} | {engineer} | {is_ka} | {hours} |".format(
                        issue=_issue_link(item),
                        customer=escape_markdown_text(item.get("customer") or "未标注客户"),
                        engineer=escape_markdown_text(item.get("engineer")),
                        is_ka=item.get("is_ka") or "未知",
                        hours=format_hours(item.get("time_spent_seconds")),
                    )
                )
            lines.append("")

    return "\n".join(lines)
