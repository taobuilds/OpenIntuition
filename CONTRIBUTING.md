# Contributing

Use Python 3.12 and install the development dependencies:

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
```

Keep changes small. A validator change should include a valid case and an invalid case that explains the behavior. Errors should name the offending field; file errors should include the line number.

For a new scenario, write the events and expected answers first. Check temporary scope and revocation against [the event rules](docs/policy_spec.md). Do not derive the reference answer from the policy being tested.

The current data are development examples. Policies receive only events up to the query step, the query key, and the session ID. Keep expected answers and future events outside that interface. Include a boundary test when changing the runner.
