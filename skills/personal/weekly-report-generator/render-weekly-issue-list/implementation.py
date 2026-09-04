#!/usr/bin/env python3
"""Render the structured weekly issue payload as Markdown."""

import argparse
import json
import sys
from datetime import date, timedelta
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

from issue_list import render_issue_list_markdown  # noqa: E402


def read_payload(input_path):
    if input_path:
        return json.loads(Path(input_path).expanduser().read_text(encoding="utf-8"))
    return json.load(sys.stdin)


def default_filename(payload):
    period = payload.get("period") or {}
    start = date.fromisoformat(period["start"])
    end_inclusive = date.fromisoformat(period["end"]) - timedelta(days=1)
    return f"weekly_issue_list_{start:%Y%m%d}_{end_inclusive:%Y%m%d}.md"


def main():
    parser = argparse.ArgumentParser(description="生成技术支持每周 Issue Markdown 列表")
    parser.add_argument("--input", help="查询阶段生成的 JSON 文件；省略时读取 stdin")
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument("--output", help="Markdown 输出文件")
    output_group.add_argument("--output-dir", help="输出目录，文件名根据统计周期自动生成")
    args = parser.parse_args()

    try:
        payload = read_payload(args.input)
        markdown = render_issue_list_markdown(payload)
        output_path = None
        if args.output:
            output_path = Path(args.output).expanduser()
        elif args.output_dir:
            output_path = Path(args.output_dir).expanduser() / default_filename(payload)
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(markdown, encoding="utf-8")
            print(output_path, file=sys.stderr)
        else:
            print(markdown)
    except (OSError, KeyError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: 无法生成 Issue 列表：{exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
