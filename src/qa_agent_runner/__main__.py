import argparse
import sys
from pathlib import Path

from qa_agent_runner.runner import format_score, run_score


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run a QA agent against golden cases and print the score."
    )
    parser.add_argument("command", choices=["run"])
    parser.add_argument("--task", required=True, type=Path)
    parser.add_argument("--cases", required=True, type=Path)
    parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Project root used to resolve fixture paths. Defaults to the parent of the task file's folder.",
    )
    args = parser.parse_args(argv)

    root = args.root
    if root is None:
        root = args.task.resolve().parent.parent
    score = run_score(args.task.resolve(), args.cases.resolve(), root.resolve())
    print(format_score(score))
    return 0 if score.passed == score.total else 1


if __name__ == "__main__":
    sys.exit(main())
