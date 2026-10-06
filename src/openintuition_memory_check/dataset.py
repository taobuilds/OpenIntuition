"""Load scenario files with line-numbered errors."""

import json
import io
from dataclasses import dataclass
import hashlib
from pathlib import Path

from .schema import Scenario, ValidationError, parse_scenario


def _unique_json_keys(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError(f"duplicate JSON field {key!r}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValidationError(f"non-standard JSON value {value}")


@dataclass(frozen=True)
class Dataset:
    scenarios: tuple[Scenario, ...]
    name: str
    sha256: str
    size_bytes: int


def load_dataset(path: str | Path) -> Dataset:
    """Read once so the evaluated data and recorded fingerprint agree."""
    path = Path(path)
    try:
        raw = path.read_bytes()
        contents = raw.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise ValidationError(f"{path}: unable to read UTF-8 data: {exc}") from exc
    scenarios = []
    seen = set()
    for line_number, line in enumerate(io.StringIO(contents, newline=None), start=1):
        try:
            if not line.strip():
                raise ValidationError("blank lines are not allowed")
            data = json.loads(
                line, object_pairs_hook=_unique_json_keys,
                parse_constant=_reject_constant,
            )
            scenario = parse_scenario(data)
            if scenario.id in seen:
                raise ValidationError(f"duplicate scenario ID {scenario.id!r}")
        except (ValidationError, json.JSONDecodeError) as exc:
            raise ValidationError(f"{path}:{line_number}: {exc}") from exc
        seen.add(scenario.id)
        scenarios.append(scenario)
    if not scenarios:
        raise ValidationError(f"{path}: dataset is empty")
    return Dataset(tuple(scenarios), path.name, hashlib.sha256(raw).hexdigest(), len(raw))


def load_scenarios(path: str | Path) -> tuple[Scenario, ...]:
    return load_dataset(path).scenarios
