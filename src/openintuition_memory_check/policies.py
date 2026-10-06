"""Local preference policies. Inputs contain events, never answer labels."""

from collections.abc import Callable

from .schema import Event

Policy = Callable[[tuple[Event, ...], str, str], str]


def naive_last_value(events: tuple[Event, ...], key: str, session_id: str) -> str:
    """Keep the last assigned value, ignoring session scope and revocation."""
    for event in reversed(events):
        if event.key == key and event.op in {"set", "temporary"}:
            return event.value
    return "ASK"


def scoped_state(events: tuple[Event, ...], key: str, session_id: str) -> str:
    """Replay changes for one key, respecting session overrides and resets."""
    permanent = "ASK"
    temporary: dict[str, str] = {}
    for event in events:
        if event.key != key:
            continue
        if event.op == "set":
            permanent = event.value
            temporary.clear()
        elif event.op == "temporary":
            temporary[event.session_id] = event.value
        elif event.op == "revoke":
            permanent = "ASK"
            temporary.clear()
    return temporary.get(session_id, permanent)


POLICIES: dict[str, Policy] = {
    "naive_last_value": naive_last_value,
    "scoped_state": scoped_state,
}
