# OpenIntuition

Small test cases for preference memory: permanent changes, session-specific exceptions, and revoked settings.

For example, a user normally wants a dark theme, but asks for a light theme during meeting S1. S1 should use light; S2 should still use dark. If the user later revokes the preference, an old setting should not silently come back.

The repository currently contains eight synthetic scenarios and a JSONL validator. Each scenario has three checkpoints with expected answers. Policy execution and scoring are the next step.

## Install

Requires Python 3.12. From the repository root on macOS or Linux:

```bash
git clone https://github.com/taobuilds/OpenIntuition.git
cd OpenIntuition
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
```

There are no runtime dependencies or API keys. The `dev` extra installs pytest for development.

## Validate data

```bash
python -m openintuition_memory_check validate --data data/scenarios.jsonl
python -m openintuition_memory_check validate --data data/scenarios.jsonl --review
```

Expected summary:

```text
Scenarios: 8
Checkpoints: 24
  distractor: 2 scenarios
  revoke: 2 scenarios
  temporary: 2 scenarios
  update: 2 scenarios
```

`--review` prints the expected answers. Validation catches malformed records, duplicate IDs, invalid operations, and out-of-range checkpoints. It does not judge whether the answers make sense; those need to be checked against the scenario.

## Data format

Each line in `data/scenarios.jsonl` is one scenario. It contains an ordered list of events and a set of labeled checkpoints.

| Operation | Effect |
| --- | --- |
| `set` | Replace a permanent preference and clear older temporary exceptions for that key |
| `temporary` | Set an exception for one session |
| `revoke` | Remove the preference and its temporary exceptions |
| `note` | Record information without changing preferences |

A checkpoint specifies the step, preference key, and session to query. `ASK` means there is no known applicable preference. These rules are choices made for this prototype, particularly the treatment of a new permanent setting.

See [the event specification](docs/policy_spec.md) and [dataset notes](data/DATASET_CARD.md) for details.

## Code layout

```text
src/openintuition_memory_check/
  schema.py     Record types and validation rules
  dataset.py    JSONL loading and file-level errors
  cli.py        Command-line interface
data/           Eight example scenarios
docs/           Event specification
tests/          Validation and command-line checks
```

## Development

```bash
python -m pytest -q
```

For a validator change, include a small example that should pass and one that should fail. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Scope

These are development fixtures, not a model leaderboard. There are no language-model calls or evaluation scores yet. The 24 checkpoints belong to eight sequences; they are not 24 independent samples.

The next comparison will test a last-value policy against a policy that handles session scope and revocation. Natural-language extraction and model adapters come later, if the cases prove useful.

## License

Code and synthetic examples are released under the [MIT license](LICENSE).
