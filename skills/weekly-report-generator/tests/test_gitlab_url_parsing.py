import importlib.util
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
IMPLEMENTATION = SKILL_DIR / "fetch-gitlab-issue-details" / "implementation.py"
SPEC = importlib.util.spec_from_file_location("fetch_gitlab_issue_details", IMPLEMENTATION)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class GitLabUrlParsingTests(unittest.TestCase):
    def test_extracts_project_from_legacy_issue_url(self):
        url = "https://jihulab.com/group/project/-/issues/123"
        self.assertEqual(MODULE.extract_project_path(url), "group/project")
        self.assertEqual(MODULE.extract_iid_from_url(url), "123")

    def test_extracts_project_from_work_item_url(self):
        url = "https://jihulab.com/group/project/-/work_items/456"
        self.assertEqual(MODULE.extract_project_path(url), "group/project")
        self.assertEqual(MODULE.extract_iid_from_url(url), "456")


if __name__ == "__main__":
    unittest.main()
