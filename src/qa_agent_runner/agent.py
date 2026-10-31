from pathlib import Path

from qa_agent_runner.models import AgentResult, Finding, Rule, TaskSpec
from qa_agent_runner.tools import StepLimitExceeded, ToolBox, ToolDenied


def run_agent(task: TaskSpec, fixture: Path) -> AgentResult:
    """One agent step. It may only use tools the task spec allows."""
    box = ToolBox(task.allowed_tools, fixture)
    try:
        metadata = box.call("read_metadata", task.max_steps)
        fields = box.call("list_fields", task.max_steps)
    except (ToolDenied, StepLimitExceeded) as exc:
        return AgentResult(verdict="error", trace=box.trace, error=str(exc))

    findings = [
        Finding(rule.id, rule.message)
        for rule in task.rules
        if rule_failed(rule, metadata, fields)
    ]
    verdict = "fail" if findings else "pass"
    return AgentResult(verdict=verdict, findings=findings, trace=box.trace)


def rule_failed(rule: Rule, metadata: dict, fields: list[str]) -> bool:
    if rule.type == "ends_with":
        actual = str(metadata.get(rule.path or "", ""))
        return not actual.endswith(rule.value or "")
    if rule.type == "non_empty":
        actual = str(metadata.get(rule.path or "", ""))
        return not actual.strip()
    if rule.type == "field_exists":
        return (rule.field_name or "") not in fields
    return True
