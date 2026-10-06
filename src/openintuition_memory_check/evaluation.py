"""Evaluate event-only policies and write reproducible local reports."""

from collections import defaultdict
from dataclasses import asdict, dataclass
import json
from pathlib import Path

from .policies import Policy
from .schema import Scenario


@dataclass(frozen=True)
class Prediction:
    policy: str
    scenario: str
    category: str
    checkpoint: str
    as_of_step: int
    key: str
    session_id: str
    expected: str
    predicted: str
    correct: bool


def evaluate(scenarios: tuple[Scenario, ...], policies: dict[str, Policy]) -> tuple[Prediction, ...]:
    predictions = []
    for name, policy in policies.items():
        for scenario in scenarios:
            for point in scenario.checkpoints:
                prefix = tuple(event for event in scenario.events if event.step <= point.as_of_step)
                predicted = policy(prefix, point.key, point.session_id)
                predictions.append(Prediction(
                    name, scenario.id, scenario.category, point.id, point.as_of_step,
                    point.key, point.session_id, point.expected, predicted,
                    predicted == point.expected,
                ))
    return tuple(predictions)


def _counts(rows: list[Prediction]) -> dict:
    correct = sum(row.correct for row in rows)
    scenarios: dict[str, list[bool]] = defaultdict(list)
    for row in rows:
        scenarios[row.scenario].append(row.correct)
    return {
        "correct": correct, "total": len(rows), "accuracy": correct / len(rows),
        "scenarios_passed": sum(all(values) for values in scenarios.values()),
        "scenarios_total": len(scenarios),
    }


def summarize(predictions: tuple[Prediction, ...]) -> dict:
    grouped: dict[str, list[Prediction]] = defaultdict(list)
    for row in predictions:
        grouped[row.policy].append(row)
    summary = {}
    for name, rows in grouped.items():
        categories = sorted({row.category for row in rows})
        summary[name] = {
            **_counts(rows),
            "categories": {category: _counts([row for row in rows if row.category == category])
                           for category in categories},
        }
    return summary


def _cell(value: str) -> str:
    return value.replace("\\", "\\\\").replace("|", "\\|").replace("\n", "<br>").replace("\r", "")


def markdown_report(predictions: tuple[Prediction, ...], summary: dict) -> str:
    lines = [
        "# OpenIntuition results", "",
        "Exact matches against authored labels. These synthetic cases test event rules; "
        "they do not measure language-model capability. Checkpoints within a scenario are related.", "",
        "| Policy | Correct checkpoints | Accuracy | Fully correct scenarios |",
        "| --- | ---: | ---: | ---: |",
    ]
    for name, counts in summary.items():
        lines.append(f"| {name} | {counts['correct']}/{counts['total']} | "
                     f"{counts['accuracy']:.1%} | {counts['scenarios_passed']}/{counts['scenarios_total']} |")
    lines.extend(["", "## By category", "", "| Policy | Category | Correct checkpoints |",
                  "| --- | --- | ---: |"])
    for name, counts in summary.items():
        for category, result in counts["categories"].items():
            lines.append(f"| {name} | {category} | {result['correct']}/{result['total']} |")
    lines.extend(["", "## Mismatches", ""])
    failures = [row for row in predictions if not row.correct]
    if not failures:
        lines.append("No mismatches.")
    else:
        lines.extend(["| Policy | Scenario | Checkpoint | Step | Key | Session | Expected | Predicted |",
                      "| --- | --- | --- | ---: | --- | --- | --- | --- |"])
        for row in failures:
            values = [row.policy, row.scenario, row.checkpoint, str(row.as_of_step),
                      row.key, row.session_id, row.expected, row.predicted]
            lines.append("| " + " | ".join(_cell(value) for value in values) + " |")
    return "\n".join(lines) + "\n"


def write_results(output: str | Path, predictions: tuple[Prediction, ...], summary: dict) -> None:
    """Create a new result directory; never overwrite an earlier run."""
    files = {
        "summary.json": json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        "predictions.jsonl": "".join(json.dumps(asdict(row), ensure_ascii=False) + "\n" for row in predictions),
        "report.md": markdown_report(predictions, summary),
    }
    directory = Path(output)
    directory.mkdir(parents=True, exist_ok=False)
    for name, contents in files.items():
        (directory / name).write_text(contents, encoding="utf-8")
