"""Policy behavior, evaluator isolation, and result files."""

from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys

import pytest

from openintuition_memory_check.dataset import load_scenarios
from openintuition_memory_check.evaluation import evaluate, summarize, write_results
from openintuition_memory_check.policies import POLICIES, naive_last_value, scoped_state
from openintuition_memory_check.schema import Checkpoint, Event, Scenario

DATA = Path(__file__).resolve().parents[1] / "data/scenarios.jsonl"


def event(step, op, value=None, session=None, key="theme"):
    return Event(f"e{step}", step, op, key, value, session)


@pytest.mark.parametrize("events,session,expected", [
    ((event(1, "note", "dark"),), "S1", "ASK"),
    ((event(1, "temporary", "light", "S1"),), "S2", "ASK"),
    ((event(1, "temporary", "light", "S1"), event(2, "temporary", "dark", "S2")), "S1", "light"),
    ((event(1, "temporary", "light", "S1"), event(2, "temporary", "dark", "S1")), "S1", "dark"),
    ((event(1, "temporary", "light", "S1"), event(2, "set", "dark")), "S1", "dark"),
    ((event(1, "set", "dark"), event(2, "temporary", "light", "S1"), event(3, "revoke")), "S1", "ASK"),
    ((event(1, "set", "dark"), event(2, "revoke"), event(3, "set", "light")), "S2", "light"),
    ((event(1, "set", "dark"), event(2, "revoke", key="language")), "S1", "dark"),
])
def test_scoped_rules(events, session, expected):
    assert scoped_state(events, "theme", session) == expected


def test_naive_baseline_ignores_scope_and_revoke_but_not_notes():
    events = (event(1, "set", "dark"), event(2, "temporary", "light", "S1"),
              event(3, "revoke"), event(4, "note", "blue"))
    assert naive_last_value(events, "theme", "S2") == "light"
    assert naive_last_value(events, "language", "S1") == "ASK"


def test_policy_receives_only_prefix_and_query_even_with_unsorted_checkpoints():
    calls = []

    def spy(events, key, session):
        calls.append((events, key, session))
        assert all(isinstance(item, Event) for item in events)
        return events[-1].value

    first, future = event(1, "set", "dark"), event(2, "set", "light")
    scenario = Scenario("0.1", "secret_id", "update", (first, future), (
        Checkpoint("later", 2, "theme", "S1", "light"),
        Checkpoint("earlier", 1, "theme", "S2", "dark"),
    ))
    predictions = evaluate((scenario,), {"spy": spy})
    assert calls == [((first, future), "theme", "S1"), ((first,), "theme", "S2")]
    changed_labels = replace(scenario, checkpoints=tuple(replace(point, expected="wrong") for point in scenario.checkpoints))
    assert [row.predicted for row in evaluate((changed_labels,), {"spy": spy})] == [row.predicted for row in predictions]
    assert all(row.correct for row in predictions)


def test_scenarios_do_not_share_state():
    first = Scenario("0.1", "first", "update", (event(1, "set", "dark"),),
                     (Checkpoint("q", 1, "theme", "S1", "dark"),))
    second = Scenario("0.1", "second", "distractor", (event(1, "note", "dark"),),
                      (Checkpoint("q", 1, "theme", "S1", "ASK"),))
    assert all(row.correct for row in evaluate((first, second), POLICIES))


def test_pilot_results_and_saved_outputs(tmp_path):
    predictions = evaluate(load_scenarios(DATA), POLICIES)
    summary = summarize(predictions)
    assert summary["naive_last_value"]["correct"] == 19
    assert summary["naive_last_value"]["scenarios_passed"] == 4
    assert summary["scoped_state"]["correct"] == 24
    assert summary["scoped_state"]["scenarios_passed"] == 8
    assert summary["naive_last_value"]["categories"]["revoke"]["correct"] == 3
    output = tmp_path / "results"
    write_results(output, predictions, summary)
    saved = [json.loads(line) for line in (output / "predictions.jsonl").read_text().splitlines()]
    assert len(saved) == 48
    assert sum(not row["correct"] for row in saved) == 5
    assert json.loads((output / "summary.json").read_text()) == summary
    assert "19/24" in (output / "report.md").read_text()
    with pytest.raises(FileExistsError):
        write_results(output, (), {})
    assert json.loads((output / "summary.json").read_text()) == summary


def test_cli_runs_one_policy_and_refuses_existing_directory(tmp_path):
    output = tmp_path / "run"
    command = [sys.executable, "-m", "openintuition_memory_check", "run", "--data", str(DATA),
               "--policy", "scoped_state", "--output", str(output)]
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 0
    assert "24/24" in result.stdout
    assert set(json.loads((output / "summary.json").read_text())) == {"scoped_state"}
    result = subprocess.run(command, capture_output=True, text=True)
    assert result.returncode == 2
    assert "Run failed" in result.stderr


def test_invalid_input_does_not_create_results(tmp_path):
    output = tmp_path / "run"
    result = subprocess.run(
        [sys.executable, "-m", "openintuition_memory_check", "run", "--data", str(tmp_path / "missing"),
         "--output", str(output)], capture_output=True, text=True,
    )
    assert result.returncode == 2
    assert not output.exists()
