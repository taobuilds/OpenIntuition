# Scenario notes

Dataset version: `pilot-0.1`. Schema version: `0.1`.

Eight fictional event sequences, with three events and three checkpoints each. The four categories—updates, temporary exceptions, revocation, and unrelated events—contain two sequences each.

## Origin and review

The examples were drafted with AI assistance, then checked against the event rules. They are fictional and contain no real conversation logs or user preferences. Expected answers are written explicitly; the validator checks their format, not their correctness.

Use `python -m openintuition_memory_check validate --data data/scenarios.jsonl --review` to read all 24 labels before changing a case. This prints expected answers, not predictions.

## Intended use and limitations

These are development examples, not a held-out benchmark. Checkpoints within one sequence are dependent. The data cover explicit settings only: no natural-language extraction, implicit preferences, time decay, multiple-user permissions, or ambiguous conflicts.

## License

The synthetic examples use the repository's [MIT license](../LICENSE).

## Extended development suite

`extended_scenarios.jsonl`, version `extended-0.1`, includes the eight pilot sequences and twelve additional sequences: **20 scenarios, 72 checkpoints**, with five scenarios and eighteen checkpoints per category. The additional sequences have four or five events and four checkpoints. They cover repeated changes, multiple session exceptions, reset after exceptions, temporary settings after revocation, distinct session IDs, and unrelated-key isolation.

The pilot is a subset of this file, not a separate held-out split. See [case review notes](../docs/CASE_REVIEW.md) for the authored answer sequence and purpose of each added case. The extended labels were specified before policy execution. They have not received independent human review.

A copy of the extended suite is packaged with the Python distribution for the `demo` command. Tests check that the packaged copy and the source dataset are identical. Reports record the exact input bytes' SHA-256 hash in `manifest.json`.
