from qa_agent_runner.models import AgentResult, CaseResult, CaseSpec


def judge(case: CaseSpec, result: AgentResult) -> CaseResult:
    """Score one agent result against a known-good case. The judge does not rerun the agent."""
    if result.verdict == "error":
        return CaseResult(
            case_id=case.id,
            passed=False,
            expected=case.expect,
            actual="error",
            reason=result.error or "agent stopped on a control error",
        )

    if result.verdict != case.expect:
        return CaseResult(
            case_id=case.id,
            passed=False,
            expected=case.expect,
            actual=result.verdict,
            reason=f"verdict was {result.verdict}, expected {case.expect}",
        )

    finding_ids = [finding.rule_id for finding in result.findings]
    if case.expect_finding and case.expect_finding not in finding_ids:
        return CaseResult(
            case_id=case.id,
            passed=False,
            expected=case.expect,
            actual=result.verdict,
            reason=f"missing finding {case.expect_finding}",
        )

    if case.expect == "pass" and finding_ids:
        return CaseResult(
            case_id=case.id,
            passed=False,
            expected=case.expect,
            actual=result.verdict,
            reason=f"expected a clean pass, found {', '.join(finding_ids)}",
        )

    return CaseResult(
        case_id=case.id,
        passed=True,
        expected=case.expect,
        actual=result.verdict,
        reason="matched the golden case",
    )
