# qa-agent-runner

A small control loop for a QA agent. The task spec commands the agent. A separate judge scores the result against cases where the right answer is already known.

This first version checks Salesforce custom-object metadata. The agent is scripted on purpose, so the score reruns with no API key. The loop around it is the part to learn: what the agent is allowed to do, when it must stop, and how a change is accepted only when the score holds.

## The loop

1. **Task spec** (`tasks/metadata_validation.json`) states the goal, the allowed tools, the step limit, and the rules.
2. **Tools** (`read_metadata`, `list_fields`) are the only way the agent can see a fixture. Any other tool call is denied.
3. **Agent** takes one step: read the metadata, list the fields, apply the rules, return `pass` or `fail` plus findings.
4. **Judge** compares that result to a golden case. It does not generate a new answer.
5. **Score** is how many cases matched. Rerun it after every change.

## Run

From this folder, with Python 3.11 or newer:

```powershell
$env:PYTHONPATH = "src"
python -m qa_agent_runner run --task tasks/metadata_validation.json --cases cases/golden.json
```

A good run looks like this:

```text
pass  valid-object          actual=pass  expected=pass  matched the golden case
pass  bad-api-name          actual=fail  expected=fail  matched the golden case
pass  empty-label           actual=fail  expected=fail  matched the golden case
pass  missing-name-field    actual=fail  expected=fail  matched the golden case
score 4/4
```

The command exits `0` when every case matches, and `1` when any case does not.

## Tests

```powershell
$env:PYTHONPATH = "src"
python -m unittest discover -s tests
```

## What to change next

Keep this score as the gate. The next step is to replace `run_agent` with a model that must still use only `allowed_tools`, stop at `max_steps`, and pass the same four cases. A prompt change stays only when `score 4/4` still holds.
