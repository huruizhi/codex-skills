import sys
import unittest
from datetime import date
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR))

from issue_list import (  # noqa: E402
    TECH_SUPPORT_ENGINEERS,
    build_issue_query,
    previous_natural_week,
    render_issue_list_markdown,
)


class PreviousNaturalWeekTests(unittest.TestCase):
    def test_uses_monday_to_monday_half_open_range(self):
        start, end = previous_natural_week(date(2026, 7, 20))

        self.assertEqual(start, date(2026, 7, 13))
        self.assertEqual(end, date(2026, 7, 20))


class QueryContractTests(unittest.TestCase):
    def test_uses_the_existing_eight_engineers_including_han_fei(self):
        self.assertEqual(
            TECH_SUPPORT_ENGINEERS,
            (
                "雷程",
                "李发富",
                "陶郭宇",
                "韩飞",
                "彭锐",
                "王凯旋",
                "张永宝",
                "胡睿智",
            ),
        )

    def test_query_aggregates_time_without_filtering_issue_type(self):
        query, engineer_params = build_issue_query(has_ka_field=True)

        self.assertIn("SUM(a.timeSpent)", query)
        self.assertIn("a.spentAt >= %s", query)
        self.assertIn("a.spentAt < %s", query)
        where_clause = query.split("WHERE", 1)[1].split("GROUP BY", 1)[0]
        self.assertNotIn("Task_type", where_clause)
        self.assertEqual(engineer_params, TECH_SUPPORT_ENGINEERS)


class MarkdownRendererTests(unittest.TestCase):
    def test_groups_by_engineer_and_ka_and_sums_duplicate_rows(self):
        payload = {
            "period": {"start": "2026-07-13", "end": "2026-07-20"},
            "engineers": list(TECH_SUPPORT_ENGINEERS),
            "items": [
                {
                    "issue_id": 11,
                    "title": "升级 | 排查",
                    "web_url": "https://jihulab.com/example/issues/11",
                    "customer": "甲客户",
                    "engineer": "韩飞",
                    "is_ka": "是",
                    "time_spent_seconds": 3600,
                },
                {
                    "issue_id": 11,
                    "title": "升级 | 排查",
                    "web_url": "https://jihulab.com/example/issues/11",
                    "customer": "甲客户",
                    "engineer": "韩飞",
                    "is_ka": "是",
                    "time_spent_seconds": 1800,
                },
                {
                    "issue_id": 11,
                    "title": "升级 | 排查",
                    "web_url": "https://jihulab.com/example/issues/11",
                    "customer": "甲客户",
                    "engineer": "雷程",
                    "is_ka": "否",
                    "time_spent_seconds": 900,
                },
            ],
        }

        markdown = render_issue_list_markdown(payload)

        self.assertIn("2026-07-13 至 2026-07-19", markdown)
        self.assertIn("## 韩飞", markdown)
        self.assertIn("### KA", markdown)
        self.assertIn("升级 \\| 排查", markdown)
        self.assertIn("1.50 小时", markdown)
        self.assertIn("## 雷程", markdown)
        self.assertIn("### 非 KA", markdown)
        self.assertIn("0.25 小时", markdown)
        self.assertEqual(markdown.count("[升级 \\| 排查]"), 2)

    def test_marks_missing_customer_mapping_as_unlinked(self):
        payload = {
            "period": {"start": "2026-07-13", "end": "2026-07-20"},
            "items": [
                {
                    "issue_id": 12,
                    "title": "无客户映射",
                    "web_url": "https://jihulab.com/example/issues/12",
                    "customer": "",
                    "engineer": "韩飞",
                    "is_ka": None,
                    "time_spent_seconds": 60,
                }
            ],
        }

        markdown = render_issue_list_markdown(payload)

        self.assertIn("### 客户未关联", markdown)
        self.assertIn("未标注客户", markdown)
        self.assertIn("客户未关联", markdown)

    def test_marks_internal_work_without_requiring_customer_mapping(self):
        payload = {
            "period": {"start": "2026-07-13", "end": "2026-07-20"},
            "items": [
                {
                    "issue_id": 13,
                    "title": "内部协作",
                    "web_url": "https://jihulab.com/example/-/work_items/13",
                    "customer": "内部任务",
                    "engineer": "韩飞",
                    "is_ka": "内部任务",
                    "time_spent_seconds": 3600,
                }
            ],
        }

        markdown = render_issue_list_markdown(payload)

        self.assertIn("### 内部任务", markdown)
        self.assertIn("| 内部任务 | 韩飞 | 内部任务 |", markdown)


if __name__ == "__main__":
    unittest.main()
