#!/usr/bin/env python3
"""Query weekly technical-support issue timelogs from MySQL."""

import argparse
import json
import os
import sys
from datetime import date, datetime, time, timezone
from pathlib import Path
from zoneinfo import ZoneInfo


SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

from issue_list import (  # noqa: E402
    TECH_SUPPORT_ENGINEERS,
    build_issue_query,
    previous_natural_week,
)


REPORT_TIMEZONE = ZoneInfo("Asia/Shanghai")


def parse_date(value):
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("日期必须使用 YYYY-MM-DD 格式") from exc


def resolve_period(anchor_date=None, start_date=None, end_date=None):
    if bool(start_date) != bool(end_date):
        raise ValueError("--start-date 和 --end-date 必须同时提供")
    if start_date and end_date:
        if start_date >= end_date:
            raise ValueError("--end-date 必须晚于 --start-date（结束日期不包含在范围内）")
        return start_date, end_date
    return previous_natural_week(anchor_date or datetime.now(REPORT_TIMEZONE).date())


def database_boundaries(start_date, end_date):
    """Convert Asia/Shanghai date boundaries to naive UTC for Django MySQL data."""
    start_local = datetime.combine(start_date, time.min, tzinfo=REPORT_TIMEZONE)
    end_local = datetime.combine(end_date, time.min, tzinfo=REPORT_TIMEZONE)
    start_utc = start_local.astimezone(timezone.utc).replace(tzinfo=None)
    end_utc = end_local.astimezone(timezone.utc).replace(tzinfo=None)
    return start_utc, end_utc


def load_db_config():
    env_names = {
        "host": "WEEKLY_REPORT_DB_HOST",
        "user": "WEEKLY_REPORT_DB_USER",
        "password": "WEEKLY_REPORT_DB_PASSWORD",
    }
    missing = [env for env in env_names.values() if not os.getenv(env)]
    if missing:
        raise RuntimeError("缺少数据库环境变量：" + ", ".join(missing))
    try:
        port = int(os.getenv("WEEKLY_REPORT_DB_PORT", "3306"))
    except ValueError as exc:
        raise RuntimeError("WEEKLY_REPORT_DB_PORT 必须是整数") from exc
    return {
        "host": os.environ[env_names["host"]],
        "port": port,
        "database": os.getenv("WEEKLY_REPORT_DB_NAME", "portal"),
        "user": os.environ[env_names["user"]],
        "password": os.environ[env_names["password"]],
    }


def connect_to_database():
    config = load_db_config()
    try:
        import mysql.connector
        from mysql.connector import Error
    except ImportError as exc:
        raise RuntimeError("缺少 mysql-connector-python，请先安装依赖") from exc
    try:
        return mysql.connector.connect(**config)
    except Error as exc:
        raise RuntimeError(f"数据库连接失败：{exc}") from exc


def database_has_ka_field(connection):
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.columns
            WHERE table_schema = DATABASE()
              AND table_name = 'gitlab_app_organizationextension'
              AND column_name = 'support_customer_type'
            """
        )
        return bool(cursor.fetchone()[0])
    finally:
        cursor.close()


def query_issues(start_at, end_at):
    connection = connect_to_database()
    cursor = connection.cursor(dictionary=True)
    try:
        has_ka_field = database_has_ka_field(connection)
        query, engineer_params = build_issue_query(has_ka_field)
        cursor.execute(query, (start_at, end_at, *engineer_params))
        rows = cursor.fetchall()
        for row in rows:
            row["time_spent_seconds"] = int(row.get("time_spent_seconds") or 0)
        return rows, has_ka_field
    finally:
        cursor.close()
        connection.close()


def build_payload(start_date, end_date, rows, has_ka_field):
    return {
        "period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "end_exclusive": True,
            "timezone": "Asia/Shanghai",
        },
        "engineers": list(TECH_SUPPORT_ENGINEERS),
        "ka_source_available": has_ka_field,
        "items": rows,
    }


def main():
    parser = argparse.ArgumentParser(description="查询上周有工时记录的技术支持 Issue")
    parser.add_argument(
        "--date",
        type=parse_date,
        help="统计锚点日期，默认今天；统计该日期所在周之前的自然周",
    )
    parser.add_argument("--start-date", type=parse_date, help="开始日期（包含）")
    parser.add_argument("--end-date", type=parse_date, help="结束日期（不包含）")
    parser.add_argument("--output", help="JSON 输出文件；省略时输出到 stdout")
    args = parser.parse_args()

    try:
        start_date, end_date = resolve_period(args.date, args.start_date, args.end_date)
        start_at, end_at = database_boundaries(start_date, end_date)
        rows, has_ka_field = query_issues(start_at, end_at)
    except (RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    payload = build_payload(start_date, end_date, rows, has_ka_field)
    output = json.dumps(payload, ensure_ascii=False, indent=2)
    if args.output:
        output_path = Path(args.output).expanduser()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
