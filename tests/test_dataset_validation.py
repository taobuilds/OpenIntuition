"""Scenario validation and command-line error handling."""

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys

import pytest

from openintuition_memory_check.dataset import load_scenarios
from openintuition_memory_check.schema import ValidationError, parse_scenario


@pytest.fixture
def sample():
    return {
        "schema_version": "0.1", "id": "independent_example", "category": "update",
        "events": [{"id": "first", "step": 1, "op": "set", "key": "font", "value": "large", "session_id": None}],
        "checkpoints": [{"id": "check", "as_of_step": 1, "key": "font", "session_id": "room", "expected": "large"}],
    }


def test_accepts_valid_scenario_and_unknown_preference_query(sample):
    sample["checkpoints"][0].update(key="unset_key", expected="ASK")
    scenario = parse_scenario(sample)
    assert scenario.events[0].value == "large"
    assert scenario.checkpoints[0].expected == "ASK"


@pytest.mark.parametrize("field,value,message", [
    ("step", True, "positive integer"),
    ("step", 2, "contiguous"),
    ("op", "unknown", "unsupported operation"),
    ("session_id", "room", "requires null"),
    ("value", " ", "non-empty string"),
    ("value", "ASK", "reserved"),
])
def test_rejects_bad_event(sample, field, value, message):
    sample["events"][0][field] = value
    with pytest.raises(ValidationError, match=message):
        parse_scenario(sample)


def test_requires_temporary_session_and_null_revoke_value(sample):
    sample["events"][0]["op"] = "temporary"
    with pytest.raises(ValidationError, match="session_id"):
        parse_scenario(sample)
    sample["events"][0]["op"] = "revoke"
    with pytest.raises(ValidationError, match="revoke requires null"):
        parse_scenario(sample)


def test_rejects_missing_and_extra_fields(sample):
    del sample["events"][0]["key"]
    with pytest.raises(ValidationError, match="missing fields"):
        parse_scenario(sample)
    sample["events"][0]["key"] = "font"
    sample["events"][0]["expected"] = "large"
    with pytest.raises(ValidationError, match="unknown fields"):
        parse_scenario(sample)


def test_rejects_future_checkpoint_and_duplicate_checkpoint_id(sample):
    sample["checkpoints"][0]["as_of_step"] = 2
    with pytest.raises(ValidationError, match="exceeds"):
        parse_scenario(sample)
    sample["checkpoints"][0]["as_of_step"] = 1
    sample["checkpoints"].append(deepcopy(sample["checkpoints"][0]))
    with pytest.raises(ValidationError, match="duplicate checkpoint"):
        parse_scenario(sample)


def test_rejects_duplicate_event_id(sample):
    extra = deepcopy(sample["events"][0])
    extra["step"] = 2
    sample["events"].append(extra)
    with pytest.raises(ValidationError, match="duplicate event"):
        parse_scenario(sample)


def test_loader_gives_line_number_for_duplicate_scenario(sample, tmp_path):
    path = tmp_path / "duplicate.jsonl"
    path.write_text((json.dumps(sample) + "\n") * 2, encoding="utf-8")
    with pytest.raises(ValidationError, match=r"duplicate.jsonl:2: duplicate scenario"):
        load_scenarios(path)


@pytest.mark.parametrize("contents,message", [
    ("", "dataset is empty"),
    ("\n", "blank lines"),
    ("{broken}\n", ":1:"),
    ('{"id":"a","id":"b"}\n', "duplicate JSON field"),
    ('{"unexpected":NaN}\n', "non-standard JSON"),
])
def test_loader_rejects_bad_jsonl(tmp_path, contents, message):
    path = tmp_path / "bad.jsonl"
    path.write_text(contents, encoding="utf-8")
    with pytest.raises(ValidationError, match=message):
        load_scenarios(path)


def test_missing_file_returns_cli_error(tmp_path):
    result = subprocess.run(
        [sys.executable, "-m", "openintuition_memory_check", "validate", "--data", str(tmp_path / "missing.jsonl")],
        capture_output=True, text=True,
    )
    assert result.returncode == 2
    assert "Validation failed" in result.stderr
    assert "Scenarios:" not in result.stdout


def test_pilot_counts_and_review():
    path = Path(__file__).resolve().parents[1] / "data/scenarios.jsonl"
    scenarios = load_scenarios(path)
    assert len(scenarios) == 8
    assert sum(len(s.checkpoints) for s in scenarios) == 24
    assert all(len(s.events) == 3 and len(s.checkpoints) == 3 for s in scenarios)
    result = subprocess.run(
        [sys.executable, "-m", "openintuition_memory_check", "validate", "--data", str(path), "--review"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "Scenarios: 8" in result.stdout
    assert "Checkpoints: 24" in result.stdout
    assert "temporary_01 | q3 | 3 | theme | S2 | dark" in result.stdout
    assert "labels, not predictions" in result.stdout
