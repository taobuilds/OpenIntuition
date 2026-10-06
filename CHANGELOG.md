# Changes

## 0.2.0

OpenIntuition now includes a self-contained browser report. Filter predictions by policy, category, scenario, or outcome; select a checkpoint to inspect its event prefix and answers. The interface supports Chinese and English and works offline without a server.

- Added twelve longer development cases. The extended suite includes 20 scenarios and 72 checkpoints; the original pilot remains unchanged.
- Added `openintuition demo --output <new-directory>` with bundled example data.
- Added `--fail-on-mismatch` for regression workflows; mismatches return code 1 without discarding reports.
- Added deterministic manifests with dataset SHA-256, tool version, counts, and selected policies.
- Failed output writes clean up files created by that run. Existing result directories are never overwritten.
- Added policy invariants, report input-boundary checks, HTML escaping checks, and browser interaction tests.
- Added automated Python checks on Linux, macOS, and Windows, plus a Chromium report check.

The scores still describe explicit event-rule conformance on synthetic development fixtures, not performance of language models or existing memory products.

## 0.1 development versions

Added the pilot dataset, strict JSONL validation, two local policies, exact-match scoring, Markdown reports, and the OpenIntuition hand-drawn owl identity.
