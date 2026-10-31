from dataclasses import dataclass, field


@dataclass
class Rule:
    id: str
    type: str
    message: str
    path: str | None = None
    value: str | None = None
    field_name: str | None = None


@dataclass
class TaskSpec:
    id: str
    goal: str
    allowed_tools: list[str]
    max_steps: int
    rules: list[Rule]


@dataclass
class Finding:
    rule_id: str
    message: str


@dataclass
class TraceEvent:
    step: int
    tool: str
    status: str
    detail: str = ""


@dataclass
class AgentResult:
    verdict: str
    findings: list[Finding] = field(default_factory=list)
    trace: list[TraceEvent] = field(default_factory=list)
    error: str | None = None


@dataclass
class CaseSpec:
    id: str
    fixture: str
    expect: str
    expect_finding: str | None = None


@dataclass
class CaseResult:
    case_id: str
    passed: bool
    expected: str
    actual: str
    reason: str


@dataclass
class Score:
    passed: int
    total: int
    cases: list[CaseResult]

    @property
    def rate(self) -> float:
        if self.total == 0:
            return 0.0
        return self.passed / self.total
