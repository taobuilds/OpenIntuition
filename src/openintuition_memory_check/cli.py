"""Command-line interface."""

import argparse
from collections import Counter
from importlib.resources import as_file, files
import sys

from . import __version__
from .dataset import load_dataset, load_scenarios
from .evaluation import evaluate, summarize, write_results
from .policies import POLICIES
from .schema import ValidationError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="openintuition",
        description="Offline checks for permanent, temporary, and revoked preferences.",
        epilog="Runs locally without a model API or API keys.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", metavar="{validate,run,demo}")

    validate = commands.add_parser("validate", help="Check scenario data and print its counts.")
    validate.add_argument("--data", required=True, help="Path to a JSONL scenario file.")
    validate.add_argument("--review", action="store_true", help="Show every checkpoint's expected answer for human review.")

    run = commands.add_parser("run", help="Compare preference policies and write a results report.")
    run.add_argument("--data", required=True, help="Path to a JSONL scenario file.")
    run.add_argument(
        "--policy", choices=("both", "naive_last_value", "scoped_state"), default="both",
        help="Which policy to evaluate (default: both).",
    )
    run.add_argument("--output", required=True, help="New directory for evaluation output.")
    run.add_argument("--fail-on-mismatch", action="store_true",
                     help="Exit with code 1 if any prediction differs from its label; still write reports.")
    demo = commands.add_parser("demo", help="Run the bundled extended examples without a data path.")
    demo.add_argument("--output", required=True, help="New directory for the demo report.")
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
    try:
        if args.command == "demo":
            resource = files("openintuition_memory_check").joinpath("resources", "extended_scenarios.jsonl")
            with as_file(resource) as path:
                dataset = load_dataset(path)
            policies = POLICIES
        else:
            dataset = load_dataset(args.data)
            policies = POLICIES if args.policy == "both" else {args.policy: POLICIES[args.policy]}
        scenarios = dataset.scenarios
        predictions = evaluate(scenarios, policies)
        summary = summarize(predictions)
        manifest = {
            "report_schema_version": "0.1", "tool_version": __version__,
            "dataset": {"name": dataset.name, "sha256": dataset.sha256,
                        "size_bytes": dataset.size_bytes},
            "scenario_count": len(scenarios),
            "checkpoint_count": sum(len(s.checkpoints) for s in scenarios),
            "policies": list(policies), "metric": "exact_match",
        }
        write_results(args.output, predictions, summary, scenarios=scenarios, manifest=manifest)
    except (ValidationError, OSError) as exc:
        print(f"Run failed: {exc}", file=sys.stderr)
        return 2
    for name, counts in summary.items():
        print(f"{name}: {counts['correct']}/{counts['total']} checkpoints "
              f"({counts['accuracy']:.1%}); "
              f"{counts['scenarios_passed']}/{counts['scenarios_total']} scenarios fully correct")
    print(f"Results: {args.output}/report.md")
    print(f"Browser report: {args.output}/report.html")
    return 1 if getattr(args, "fail_on_mismatch", False) and any(not row.correct for row in predictions) else 0
