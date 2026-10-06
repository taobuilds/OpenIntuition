"""Command-line interface."""

import argparse
from collections import Counter
import sys

from . import __version__
from .dataset import load_scenarios
from .schema import ValidationError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m openintuition_memory_check",
        description="Offline checks for permanent, temporary, and revoked preferences.",
        epilog="Validation is available. Policy execution and scoring are not implemented yet.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", metavar="{validate,run}")

    validate = commands.add_parser("validate", help="Check scenario data and print its counts.")
    validate.add_argument("--data", required=True, help="Path to a JSONL scenario file.")
    validate.add_argument("--review", action="store_true", help="Show every checkpoint's expected answer for human review.")

    run = commands.add_parser("run", help="Compare preference policies (not yet implemented).")
    run.add_argument("--data", required=True, help="Path to a JSONL scenario file.")
    run.add_argument(
        "--policy", choices=("both", "naive_last_value", "scoped_state"), default="both",
        help="Which policy to evaluate (default: both).",
    )
    run.add_argument("--output", required=True, help="New directory for evaluation output.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 0
    if args.command == "validate":
        try:
            scenarios = load_scenarios(args.data)
        except ValidationError as exc:
            print(f"Validation failed: {exc}", file=sys.stderr)
            return 2
        counts = Counter(scenario.category for scenario in scenarios)
        print("Validation passed (structure only; expected answers require human review).")
        print(f"Scenarios: {len(scenarios)}")
        print(f"Checkpoints: {sum(len(s.checkpoints) for s in scenarios)}")
        for category, count in sorted(counts.items()):
            print(f"  {category}: {count} scenarios")
        if args.review:
            print("\nExpected-answer review (labels, not predictions):")
            print("scenario | checkpoint | step | key | session | expected")
            for scenario in scenarios:
                for point in scenario.checkpoints:
                    print(f"{scenario.id} | {point.id} | {point.as_of_step} | {point.key} | {point.session_id} | {point.expected}")
        return 0
    parser.error(
        f"'{args.command}' is not implemented yet. "
        "Use 'validate' to check a scenario file."
    )
    return 2
