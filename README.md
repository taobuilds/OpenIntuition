<p align="center">
  <img src="assets/openintuition-banner.png" alt="OpenIntuition — When preferences change, memory should too." width="960">
</p>

# OpenIntuition

**A small, local test bench for preference memory.**

People change their minds. A memory system should know which preferences changed, which apply only to this session, and which were withdrawn. OpenIntuition turns those situations into explicit event sequences, runs preference policies against them, and shows exactly where the answers differ.

[简体中文](README.zh-CN.md) · [Getting started in Chinese](docs/GETTING_STARTED.zh-CN.md) · [Example results](docs/example_results.md) · [Event rules](docs/policy_spec.md) · [Contributing](CONTRIBUTING.md)

**Current version:** `0.1.0.dev2` · Python 3.12 · MIT · No runtime dependencies · No API keys

## A preference is more than its last value

Imagine this history:

> “I normally use dark mode.”
>
> “For this meeting in session S1, use light mode.”
>
> Later, in session S2: “Which theme should I use?”

The last assigned value is `light`. The applicable preference for S2 is still `dark`. A temporary request in one session should not silently become everyone's new default.

Revocation creates another problem. After “Forget my theme preference,” returning an older `dark` setting is still wrong. Under this project's rules, the answer is `ASK`: there is no known applicable preference.

These are the small mistakes this project makes visible.

## What works today

- Validate UTF-8 JSONL scenarios and report errors with file and line numbers.
- Run two local policies: a last-value baseline and a policy that respects session scope and revocation.
- Score exact matches overall and by scenario category.
- Track how many complete scenarios have no wrong answers.
- Save every prediction and a readable report of mismatches.
- Keep future events and expected answers outside each policy's input.

The included pilot has **8 fictional scenarios and 24 labeled checkpoints**, covering updates, temporary exceptions, revocation, and unrelated events. This is an early development tool. It currently operates on structured events; it does not extract preferences from chat messages or call a language model.

## Quick start

Use **Python 3.12**. The current package supports `>=3.12,<3.13`. Check `python3 --version` before installing. The commands below are for macOS or Linux.

```bash
git clone https://github.com/taobuilds/OpenIntuition.git
cd OpenIntuition

python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'

python -m openintuition_memory_check validate --data data/scenarios.jsonl
python -m openintuition_memory_check run --data data/scenarios.jsonl --policy both --output results/first-run
```

You should see:

```text
naive_last_value: 19/24 checkpoints (79.2%); 4/8 scenarios fully correct
scoped_state: 24/24 checkpoints (100.0%); 8/8 scenarios fully correct
Results: results/first-run/report.md
```

Open `results/first-run/report.md` to inspect the errors. Use a **new output directory** for every run, such as `results/second-run`; the runner refuses to overwrite an existing one.

No API key or model service is needed. Installation downloads development tools; evaluation runs locally without network access. The `dev` extra installs pytest. For regular use without pytest, install with `python -m pip install -e .`.

The Python module is still named `openintuition_memory_check`, so earlier commands remain usable after the project was renamed to OpenIntuition.

## The two policies

| Policy | Behavior | What it deliberately misses |
| --- | --- | --- |
| `naive_last_value` | Returns the latest `set` or `temporary` value for the queried key | Session boundaries and revocation |
| `scoped_state` | Replays permanent settings, session overrides, and revocation | Natural-language interpretation; it only handles explicit events |

Both policies ignore `note` events and unrelated keys. The baseline is deliberately simple so the comparison isolates scope and revocation mistakes. It is not an implementation of, or a comparison against, another memory product.

To run one policy:

```bash
python -m openintuition_memory_check run --data data/scenarios.jsonl --policy scoped_state --output results/scoped-only
```

## Read the results

On the included `pilot-0.1` data:

| Category | Checkpoints | Last-value baseline | Scoped state |
| --- | ---: | ---: | ---: |
| Permanent updates | 6 | 6/6 | 6/6 |
| Temporary exceptions | 6 | 4/6 | 6/6 |
| Revocation | 6 | 3/6 | 6/6 |
| Unrelated events | 6 | 6/6 | 6/6 |
| **Total** | **24** | **19/24 (79.2%)** | **24/24 (100.0%)** |

The baseline makes five errors: two temporary settings leak into other sessions, and three answers retain a withdrawn preference. It gets every checkpoint right in 4 of the 8 scenarios; scoped state does so in all 8.

**The 100% score is a rule-conformance check.** The scoped policy implements the specification used to author these labels. This score does not establish performance on real conversations, generalization to unseen histories, or better AI memory. The three checkpoints in a scenario share a history, so 24 checkpoints are not 24 independent experiments.

### Output files

| File | Contents | Useful for |
| --- | --- | --- |
| `report.md` | Overall scores, category counts, and mismatches | Reading the result and debugging a specific failure |
| `predictions.jsonl` | One row per policy and checkpoint | Filtering or analyzing individual answers |
| `summary.json` | Aggregate metrics per policy and category | Reading results from another program |

A comparison with both policies produces **48 prediction rows**. Each row records the policy, scenario, category, checkpoint, query step, key, session, expected answer, prediction, and whether it matched.

A mismatch looks like this:

```json
{"policy":"naive_last_value","scenario":"temporary_01","category":"temporary","checkpoint":"q3","as_of_step":3,"key":"theme","session_id":"S2","expected":"dark","predicted":"light","correct":false}
```

`expected` is an authored label. `predicted` is computed by the policy. A checkpoint passes only when the two strings match exactly. See [the full example report](docs/example_results.md).

A completed comparison exits with code `0`, even when a policy makes mistakes. Invalid input or an output-directory error returns code `2`.

## How a scenario works

Each JSONL line is one independent scenario with events and checkpoints. Events describe what happened; checkpoints ask what should apply at a particular step.

| Operation | Effect |
| --- | --- |
| `set` | Replace the permanent preference and clear older temporary exceptions for that key |
| `temporary` | Override a preference in one named session |
| `revoke` | Clear the permanent preference and all its temporary exceptions |
| `note` | Record information without changing preferences |

A session-specific value takes precedence over the permanent value in its own session. No applicable value means `ASK`. Clearing temporary overrides after a new permanent `set` is an explicit choice of this prototype, not a universal memory rule. There is no expiry clock or session-end event yet.

For example, this complete record sets a global preference and asks about it:

```json
{"schema_version":"0.1","id":"theme_example","category":"update","events":[{"id":"e1","step":1,"op":"set","key":"theme","value":"dark","session_id":null}],"checkpoints":[{"id":"q1","as_of_step":1,"key":"theme","session_id":"S1","expected":"dark"}]}
```

Event steps start at 1 and must be contiguous. Checkpoints cannot query a future step beyond the scenario's final event. Fields are strict; duplicate IDs, duplicate JSON keys, blank lines, and malformed records are rejected. Validation checks structure, not whether a reference answer is correct.

Review the existing labels with:

```bash
python -m openintuition_memory_check validate --data data/scenarios.jsonl --review
```

See [the full event specification](docs/policy_spec.md) and [dataset origin and limitations](data/DATASET_CARD.md). The fictional data were drafted with AI assistance and checked against the stated rules; they contain no real conversation logs.

## How evaluation avoids answer leakage

For each checkpoint, the runner takes only the event prefix ending at `as_of_step`. A policy receives three arguments: that event tuple, the query key, and the session ID. It does not receive expected labels, scenario metadata, checkpoints, or later events.

Each query is evaluated from its own event prefix. State does not carry between independent scenarios. This boundary is covered by tests; it is an interface constraint within one Python process, not a sandbox for untrusted code.

## Project layout

```text
assets/                            Mascot, banner, and design notes
data/
  scenarios.jsonl                  Eight fictional event histories
  DATASET_CARD.md                  Data provenance and limitations
docs/
  policy_spec.md                   Event and query semantics
  example_results.md               Report from the included pilot
  GETTING_STARTED.zh-CN.md          Chinese walkthrough
src/openintuition_memory_check/
  schema.py                        Record types and validation rules
  dataset.py                       JSONL loading and file errors
  policies.py                      The two preference policies
  evaluation.py                    Predictions, scoring, and reports
  cli.py                           Command-line interface
tests/                             Validation, policy, and input-boundary checks
```

## Development and troubleshooting

```bash
python -m pytest -q
```

Start with `policies.py` to understand the behavior, then `evaluation.py` to follow scoring. See [CONTRIBUTING.md](CONTRIBUTING.md) for changes to scenarios, validation, and policy inputs.

| Problem | What to check |
| --- | --- |
| `No module named openintuition_memory_check` | Activate `.venv` and install the project in that environment |
| Unsupported Python version | Use Python 3.12; confirm the interpreter before creating `.venv` |
| Output directory already exists | Choose a new directory; the runner preserves earlier results |
| Data file cannot be found | Run from the repository root or pass the file's full path |
| A record fails validation | Use the reported line number and field to fix that record |
| A policy disagrees with an expected label | Review the event rules and the label before changing either one |

## Next steps

- [x] Structured scenarios and strict validation
- [x] Local policy comparison with checkpoint and scenario scores
- [x] Per-prediction output and readable mismatch reports
- [ ] Longer histories, repeated overrides, and more combinations of keys
- [ ] Independently reviewed evaluation cases
- [ ] Additional policies behind the same event-only interface
- [ ] Natural-language extraction and optional model adapters

The immediate priority is better coverage of explicit preference changes. Adding model calls will be useful only when the cases and scoring are worth trusting.

## The mascot

The little teal owl is OpenIntuition's project mascot. Its ring-shaped eyes suggest observation and memory; the amber spark suggests intuition. The [transparent logo](assets/openintuition-logo.png) and [README banner](assets/openintuition-banner.png) are included in the repository, with [design notes and generation prompts](assets/README.md).

## License

Code, synthetic examples, and project artwork are provided under the [MIT license](LICENSE).
