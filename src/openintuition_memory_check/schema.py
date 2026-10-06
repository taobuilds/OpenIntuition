"""Preference records and validation rules."""

from dataclasses import dataclass


class ValidationError(ValueError):
    """A record does not match the scenario format."""


@dataclass(frozen=True)
class Event:
    id: str
    step: int
    op: str
    key: str
    value: str | None
    session_id: str | None


@dataclass(frozen=True)
class Checkpoint:
    id: str
    as_of_step: int
    key: str
    session_id: str
    expected: str


@dataclass(frozen=True)
class Scenario:
    schema_version: str
    id: str
    category: str
    events: tuple[Event, ...]
    checkpoints: tuple[Checkpoint, ...]


def _fields(value: object, required: set[str], location: str) -> dict:
    if not isinstance(value, dict):
        raise ValidationError(f"{location}: expected an object")
    missing = required - value.keys()
    extra = value.keys() - required
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing fields {sorted(missing)}")
        if extra:
            details.append(f"unknown fields {sorted(extra)}")
        raise ValidationError(f"{location}: {'; '.join(details)}")
    return value


def _text(value: object, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{location}: expected a non-empty string")
    return value


def _positive_int(value: object, location: str) -> int:
    if type(value) is not int or value < 1:
        raise ValidationError(f"{location}: expected a positive integer")
    return value


def _items(value: object, location: str) -> list:
    if not isinstance(value, list) or not value:
        raise ValidationError(f"{location}: expected a non-empty array")
    return value


def parse_scenario(value: object) -> Scenario:
    """Validate one decoded record and return immutable scenario data."""
    data = _fields(value, {"schema_version", "id", "category", "events", "checkpoints"}, "scenario")
    if data["schema_version"] != "0.1":
        raise ValidationError("schema_version: supported version is '0.1'")
    scenario_id = _text(data["id"], "id")
    category = _text(data["category"], "category")
    if category not in {"update", "temporary", "revoke", "distractor"}:
        raise ValidationError(f"category: unsupported value {category!r}")

    events = []
    event_ids = set()
    for index, item in enumerate(_items(data["events"], "events"), start=1):
        loc = f"events[{index}]"
        event = _fields(item, {"id", "step", "op", "key", "value", "session_id"}, loc)
        event_id = _text(event["id"], f"{loc}.id")
        if event_id in event_ids:
            raise ValidationError(f"{loc}.id: duplicate event ID {event_id!r}")
        event_ids.add(event_id)
        step = _positive_int(event["step"], f"{loc}.step")
        if step != index:
            raise ValidationError(f"{loc}.step: steps must be contiguous from 1; expected {index}")
        op = _text(event["op"], f"{loc}.op")
        if op not in {"set", "temporary", "revoke", "note"}:
            raise ValidationError(f"{loc}.op: unsupported operation {op!r}")
        key = _text(event["key"], f"{loc}.key")
        if op == "revoke":
            if event["value"] is not None:
                raise ValidationError(f"{loc}.value: revoke requires null")
            event_value = None
        else:
            event_value = _text(event["value"], f"{loc}.value")
            if op in {"set", "temporary"} and event_value == "ASK":
                raise ValidationError(f"{loc}.value: ASK is reserved for no known preference")
        if op == "temporary":
            session = _text(event["session_id"], f"{loc}.session_id")
        else:
            if event["session_id"] is not None:
                raise ValidationError(f"{loc}.session_id: {op} requires null")
            session = None
        events.append(Event(event_id, step, op, key, event_value, session))

    checkpoints = []
    checkpoint_ids = set()
    for index, item in enumerate(_items(data["checkpoints"], "checkpoints"), start=1):
        loc = f"checkpoints[{index}]"
        checkpoint = _fields(item, {"id", "as_of_step", "key", "session_id", "expected"}, loc)
        checkpoint_id = _text(checkpoint["id"], f"{loc}.id")
        if checkpoint_id in checkpoint_ids:
            raise ValidationError(f"{loc}.id: duplicate checkpoint ID {checkpoint_id!r}")
        checkpoint_ids.add(checkpoint_id)
        step = _positive_int(checkpoint["as_of_step"], f"{loc}.as_of_step")
        if step > len(events):
            raise ValidationError(f"{loc}.as_of_step: exceeds final event step {len(events)}")
        checkpoints.append(Checkpoint(
            checkpoint_id, step,
            _text(checkpoint["key"], f"{loc}.key"),
            _text(checkpoint["session_id"], f"{loc}.session_id"),
            _text(checkpoint["expected"], f"{loc}.expected"),
        ))
    return Scenario("0.1", scenario_id, category, tuple(events), tuple(checkpoints))
