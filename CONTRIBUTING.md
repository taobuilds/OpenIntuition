# Contributing

Use Python 3.12 and install the development dependencies:

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
```

Keep changes small. A validator change should include a valid case and an invalid case that explains the behavior. Errors should name the offending field; file errors should include the line number.

For a new scenario, write the events and expected answers first. Check temporary scope and revocation against [the event rules](docs/policy_spec.md). Do not derive the reference answer from the policy being tested.

The current data are development examples. Policies receive only events up to the query step, the query key, and the session ID. Keep expected answers and future events outside that interface. Include a boundary test when changing the runner.

## Reports and packaged examples

When changing the extended fixtures, update both `data/extended_scenarios.jsonl` and the packaged copy in `src/openintuition_memory_check/resources/`. Author labels before running a policy and document the case in `docs/CASE_REVIEW.md`. These fixtures are not a held-out benchmark.

Generate the public browser example with `python scripts/update_demo.py`. The template must keep dataset content inert: use textContent for visible text, and escape `<` in embedded JSON to prevent closing its script element. Browser histories must contain only the selected query's event prefix.

Run the optional browser smoke check after report changes:

```bash
python -m pip install playwright
python -m playwright install chromium
python scripts/check_browser_report.py docs/index.html
```

The CI workflow tests normal installation on three operating systems and runs the browser check on Linux. Runtime dependencies should remain empty until there is a concrete reason to add one.
