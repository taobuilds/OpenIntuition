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
