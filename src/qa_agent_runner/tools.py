import json
from pathlib import Path

from qa_agent_runner.models import TraceEvent


class ToolDenied(Exception):
    """The agent asked for a tool the task spec does not allow."""


class StepLimitExceeded(Exception):
    """The agent used more tool calls than the task spec allows."""


class ToolBox:
    """The only way the agent is allowed to touch a fixture."""

    def __init__(self, allowed_tools: list[str], fixture: Path) -> None:
        self.allowed = set(allowed_tools)
        self.fixture = fixture
        self.trace: list[TraceEvent] = []
        self.steps = 0
        self._metadata: dict | None = None

    def call(self, name: str, max_steps: int):
        step = self.steps + 1
        if step > max_steps:
            self.steps = step
            self.trace.append(
                TraceEvent(step, name, "blocked", f"max_steps is {max_steps}")
            )
            raise StepLimitExceeded(
                f"Stopped at step {step}: max_steps is {max_steps}"
            )
        if name not in self.allowed:
            self.steps = step
            self.trace.append(
                TraceEvent(step, name, "denied", "tool is not in allowed_tools")
            )
            raise ToolDenied(f"Tool '{name}' is not in allowed_tools")

        self.steps = step
        if name == "read_metadata":
            result = self._read_metadata()
        elif name == "list_fields":
            result = self._list_fields()
        else:
            self.trace.append(TraceEvent(step, name, "error", "unknown tool"))
            raise ToolDenied(f"Tool '{name}' is not implemented")

        self.trace.append(TraceEvent(step, name, "ok"))
        return result

    def _read_metadata(self) -> dict:
        if self._metadata is None:
            self._metadata = json.loads(self.fixture.read_text(encoding="utf-8"))
        return self._metadata

    def _list_fields(self) -> list[str]:
        metadata = self._read_metadata()
        names = []
        for field in metadata.get("fields", []):
            full_name = field.get("fullName")
            if isinstance(full_name, str):
                names.append(full_name)
        return names
