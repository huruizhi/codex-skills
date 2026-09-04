#!/usr/bin/env python3
"""
Generate Tech Support Weekly Report
Uses OpenRouter API to generate structured weekly report from classified issue data.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from openai import OpenAI


# Default model (using Anthropic Claude via OpenRouter)
DEFAULT_MODEL = "anthropic/claude-3.5-sonnet"

# Output directory
OUTPUT_DIR = os.path.expanduser(
    os.getenv("WEEKLY_REPORT_OUTPUT_DIR", "~/Documents/Obsidian/05-Work/weekly")
)

# OpenRouter configuration
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"

# Stage 1: Generate table prompt
STAGE1_PROMPT = """将下面的本周工作进展进行整理汇总成一个表格：
1. 表格使用 markdown 表格的形式输出。
2. 表格包含列：序号、客户名称、故障信息、历史信息、本周进展
3. 只输出整理后的表格，不要输出任何的解释、说明、询问等其他信息。
4. 字节客户写 替换成 荣联科技集团股份有限公司

{本周工作内容}
"""

# Stage 2: Generate report prompt
STAGE2_PROMPT = """根据上面表格信息输出内容仅包含以下部分：

一、摘要：概述本周期整体处理的**问题数量**、支持的**客户数量**及关键成果。（必须统计出来数字）

二、总体工作概述：总结部门整体技术支持方向、优化重点、关键客户类型及整体趋势。字数控制在400字以内，内容可直接用于管理层汇报。

三、客户支持情况汇总：以客户为单位，描述背景、处理过程、结论或计划，要求总结输出所有的故障排查信息；（**重要：每一个问题都要进行总结**）

> 格式要求如下：
> 以"本周期共支持约 X 家企业客户，覆盖行业..."开头，简要说明客户数量与行业范围；
> 每个客户以"客户名称："开头，后接一至两句话，说明：
>   - 背景（问题类型或支持方向）
>   - 处理过程（排查、验证、优化或沟通措施）
>   - 结论或计划（结果、客户反馈、下一步动作）；
> 语气正式、简洁、专业，避免口语；
> 不使用表格、不出现负责人或客户隐私；
> 使用 markdown 项目符号（-）列表格式，确保条理清晰；
> 每条客户描述控制在 2–3 句之间，必要时合并同一客户重复项；

四、总结与落款：总结团队价值与影响，最后一行为"专业技术服务部 + {日期}"。

要求：
- 使用正式、专业语言；
- 不使用表格、不出现负责人或客户敏感信息；
- 禁止输出任何图片或表情；
- 输出格式使用 markdown；
- 内容可直接用于公司内部汇报或周报邮件。

{表格内容}
"""


def get_api_key():
    """Get the OpenRouter API key from the environment."""
    return os.environ.get('OPENROUTER_API_KEY') or os.environ.get('ANTHROPIC_API_KEY')


def format_work_items(items: List[Dict[str, Any]]) -> str:
    """
    Format work items for prompt.

    Args:
        items: List of classified issue items

    Returns:
        Formatted string for prompt
    """
    formatted = []
    for item in items:
        title = item.get('title', '无标题')
        current_work = item.get('本周工作', [])
        history = item.get('历史回顾', [])

        formatted.append(f"## {title}")
        if current_work:
            formatted.append(f"本周工作:")
            for work in current_work:
                formatted.append(f"  - {work}")
        if history:
            formatted.append(f"历史回顾:")
            for hist in history:
                formatted.append(f"  - {hist}")
        formatted.append("")

    return "\n".join(formatted)


def call_llm(api_key: str, prompt: str, model: str = DEFAULT_MODEL) -> str:
    """
    Call OpenRouter API with prompt.

    Args:
        api_key: OpenRouter API key
        prompt: Prompt to send
        model: Model to use

    Returns:
        Response text
    """
    try:
        client = OpenAI(
            base_url=OPENROUTER_API_BASE,
            api_key=api_key,
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            max_tokens=8192,
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"Error calling OpenRouter API: {e}", file=sys.stderr)
        sys.exit(1)


def generate_report(items: List[Dict[str, Any]], api_key: str, report_date: str, model: str = None) -> Tuple[str, str]:
    """
    Generate complete weekly report from classified items.

    Args:
        items: List of classified issue items
        api_key: OpenRouter API key
        report_date: Report date string (YYYY-MM-DD)
        model: Model to use (optional)

    Returns:
        Tuple of (table_content, report_content)
    """
    if model is None:
        model = DEFAULT_MODEL

    print("Stage 1/2: Generating table...", file=sys.stderr)

    # Stage 1: Generate table
    work_content = format_work_items(items)
    stage1_prompt = STAGE1_PROMPT.format(本周工作内容=work_content)
    table = call_llm(api_key, stage1_prompt, model)

    print("Stage 2/2: Generating report...", file=sys.stderr)

    # Stage 2: Generate report with date
    stage2_prompt = STAGE2_PROMPT.format(表格内容=table, 日期=report_date)
    report = call_llm(api_key, stage2_prompt, model)

    return table, report


def save_report(table: str, report: str, report_date: str, output_dir: str = None) -> Tuple[str, str]:
    """
    Save table and report to files.

    Args:
        table: Table content
        report: Report content
        report_date: Report date string (YYYY-MM-DD)
        output_dir: Output directory (uses default if None)

    Returns:
        Tuple of (table_file_path, report_file_path)
    """
    if output_dir is None:
        output_dir = OUTPUT_DIR

    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Convert date format: YYYY-MM-DD -> YYYYMMDD
    date_suffix = report_date.replace('-', '')

    # File paths
    table_file = os.path.join(output_dir, f"weekly_report_table_{date_suffix}.md")
    report_file = os.path.join(output_dir, f"weekly_report_{date_suffix}.md")

    # Save table
    with open(table_file, 'w', encoding='utf-8') as f:
        f.write(table)

    # Save report
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

    return table_file, report_file


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Generate tech support weekly report using OpenRouter API'
    )
    parser.add_argument(
        '--input',
        type=str,
        help='Input JSON file with classified issues (reads from stdin if not provided)'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        default=OUTPUT_DIR,
        help=f'Output directory (default: {OUTPUT_DIR})'
    )
    parser.add_argument(
        '--api-key',
        type=str,
        help='OpenRouter API key (uses OPENROUTER_API_KEY env var if not provided)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default=DEFAULT_MODEL,
        help=f'Model to use (default: {DEFAULT_MODEL})'
    )
    parser.add_argument(
        '--date',
        type=str,
        help='Report date in YYYY-MM-DD format (default: today)'
    )
    parser.add_argument(
        '--table-only',
        action='store_true',
        help='Only generate table, not full report'
    )

    args = parser.parse_args()

    # Get API key
    api_key = args.api_key or get_api_key()
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable not set", file=sys.stderr)
        print("Get your API key at: https://openrouter.ai/", file=sys.stderr)
        sys.exit(1)

    # Determine report date
    if args.date:
        try:
            report_date = args.date  # Validate format
            datetime.strptime(args.date, '%Y-%m-%d')
        except ValueError:
            print(f"Error: Invalid date format '{args.date}'. Use YYYY-MM-DD.", file=sys.stderr)
            sys.exit(1)
    else:
        report_date = datetime.now().strftime('%Y-%m-%d')

    # Read input
    if args.input:
        try:
            with open(args.input, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in input file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            data = json.load(sys.stdin)
        except json.JSONDecodeError:
            print("Error: Invalid JSON from stdin", file=sys.stderr)
            sys.exit(1)

    # Extract items
    items = data.get('items', [])
    if not items:
        print("Error: No items found in input data", file=sys.stderr)
        sys.exit(1)

    print(f"Generating report for {len(items)} issues (date: {report_date})...", file=sys.stderr)

    # Generate report
    table, report = generate_report(items, api_key, report_date, args.model)

    # Save to files
    table_file, report_file = save_report(table, report, report_date, args.output_dir)

    print(f"\n✅ Report generated successfully!", file=sys.stderr)
    print(f"📊 Table: {table_file}", file=sys.stderr)
    print(f"📝 Report: {report_file}", file=sys.stderr)

    # Also output report to stdout for piping
    if not args.table_only:
        print("\n" + "="*80)
        print(report)


if __name__ == '__main__':
    main()
