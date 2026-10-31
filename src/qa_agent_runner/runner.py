import json
from pathlib import Path

from qa_agent_runner.agent import run_agent
from qa_agent_runner.judge import judge
from qa_agent_runner.models import CaseSpec, Rule, Score, TaskSpec


def load_task(path: Path) -> TaskSpec:
    raw = json.loads(path.read_text(encoding="utf-8"))
    rules = [
        Rule(
            id=rule["id"],
            type=rule["type"],
            message=rule["message"],
            path=rule.get("path"),
            value=rule.get("value"),
            field_name=rule.get("field"),
        )
        for rule in raw["rules"]
    ]
    return TaskSpec(
        id=raw["id"],
        goal=raw["goal"],
        allowed_tools=list(raw["allowed_tools"]),
        max_steps=int(raw["max_steps"]),
        rules=rules,
    )


def load_cases(path: Path) -> list[CaseSpec]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return [
        CaseSpec(
            id=case["id"],
            fixture=case["fixture"],
            expect=case["expect"],
            expect_finding=case.get("expect_finding"),
        )
        for case in raw
    ]


def run_score(task_path: Path, cases_path: Path, root: Path | None = None) -> Score:
    root = root or task_path.parent.parent
    task = load_task(task_path)
    cases = load_cases(cases_path)
    results = []
    for case in cases:
        fixture = root / case.fixture
        agent_result = run_agent(task, fixture)
        results.append(judge(case, agent_result))
    passed = sum(1 for result in results if result.passed)
    return Score(passed=passed, total=len(results), cases=results)


def format_score(score: Score) -> str:
    lines = []
    for case in score.cases:
        mark = "pass" if case.passed else "FAIL"
        lines.append(
            f"{mark:4}  {case.case_id:20}  actual={case.actual:4}  expected={case.expected:4}  {case.reason}"
        )
    lines.append(f"score {score.passed}/{score.total}")
    return "\n".join(lines)
