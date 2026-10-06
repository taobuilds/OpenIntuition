# OpenIntuition

Small test cases for preference memory: permanent changes, session-specific exceptions, and revoked settings.

For example, a user normally wants a dark theme, but asks for a light theme during meeting S1. S1 should use light; S2 should still use dark. If the user later revokes the preference, an old setting should not silently come back.

The repository contains eight synthetic scenarios, a JSONL validator, and a runner that compares two local preference policies. Each scenario has three checkpoints with authored expected answers.

中文上手说明：[运行第一个比较并读懂结果](docs/GETTING_STARTED.zh-CN.md)。

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

## Compare policies

```bash
python -m openintuition_memory_check run --data data/scenarios.jsonl --policy both --output results/first-run
```

The output directory must be new. Reusing it returns an error so an earlier run cannot be overwritten. A completed run exits successfully even if a policy has mismatches; input or output errors return exit code 2.

| Policy | Correct checkpoints | Fully correct scenarios |
| --- | ---: | ---: |
| `naive_last_value` | 19/24 (79.2%) | 4/8 |
| `scoped_state` | 24/24 (100.0%) | 8/8 |

`naive_last_value` keeps the last set/temporary value for a key, ignoring session scope and revocation. `scoped_state` replays the specified rules. Both ignore notes. This baseline comparison isolates two specific mistakes; it is not a comparison against an existing memory product.

The runner writes three files:

- `report.md`: overall results, category counts, and each mismatch.
- `predictions.jsonl`: one prediction per policy and checkpoint, including the expected answer.
- `summary.json`: checkpoint accuracy and fully correct scenario counts per policy and category.

See [the example report](docs/example_results.md). To run just one policy, use `--policy scoped_state` or `--policy naive_last_value`. Every query receives only events up to its step, the preference key, and the session ID. Expected answers and future events stay outside the policy input.

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
  policies.py   Last-value and scoped-state policies
  evaluation.py Prediction, scoring, and report output
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

These are development fixtures, not a model leaderboard. The scores compare two local rule-based programs; there are no language-model calls. The 24 checkpoints belong to eight sequences; they are not 24 independent samples. The scoped policy implements the same specification used to author the labels, so its perfect score is a conformance check, not evidence of generalization.

The next step is to expand cases with longer histories, repeated overrides, and multiple keys before adding natural-language extraction or model adapters.

## License

Code and synthetic examples are released under the [MIT license](LICENSE).
