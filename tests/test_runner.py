import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from qa_agent_runner.agent import run_agent  # noqa: E402
from qa_agent_runner.models import TaskSpec  # noqa: E402
from qa_agent_runner.runner import load_task, run_score  # noqa: E402
from qa_agent_runner.tools import ToolBox, ToolDenied  # noqa: E402


class ScoreTests(unittest.TestCase):
    def test_golden_cases_all_pass(self) -> None:
        score = run_score(
            ROOT / "tasks" / "metadata_validation.json",
            ROOT / "cases" / "golden.json",
            ROOT,
        )
        self.assertEqual(score.passed, score.total)
        self.assertEqual(score.total, 4)

    def test_disallowed_tool_is_denied(self) -> None:
        box = ToolBox(["read_metadata"], ROOT / "fixtures" / "valid_object.json")
        with self.assertRaises(ToolDenied):
            box.call("list_fields", max_steps=4)
        self.assertEqual(box.trace[0].status, "denied")

    def test_step_limit_stops_the_agent(self) -> None:
        task = load_task(ROOT / "tasks" / "metadata_validation.json")
        limited = TaskSpec(
            id=task.id,
            goal=task.goal,
            allowed_tools=task.allowed_tools,
            max_steps=1,
            rules=task.rules,
        )
        result = run_agent(limited, ROOT / "fixtures" / "valid_object.json")
        self.assertEqual(result.verdict, "error")
        self.assertIn("max_steps", result.error or "")


if __name__ == "__main__":
    unittest.main()
