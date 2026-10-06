# Preference event rules

Schema version: `0.1`. Each UTF-8 JSONL line is one independent scenario with exactly these fields: `schema_version`, `id`, `category`, `events`, `checkpoints`. Categories are `update`, `temporary`, `revoke`, and `distractor`. Lists must be non-empty, but the validator supports datasets of different sizes; it does not hardcode eight scenarios or three checkpoints.

Events contain `id`, `step`, `op`, `key`, `value`, `session_id`. Steps must follow 1, 2, 3, … in array order, without gaps. IDs are unique within their scenario. Strings are non-empty. Extra fields are rejected. JSON duplicate keys, NaN, blank lines, and unsupported schema versions are rejected.

| Operation | Meaning | Required value | Required session |
| --- | --- | --- | --- |
| set | Replace global preference for this key and clear its previous temporary exceptions | Non-empty string, except reserved ASK | null |
| temporary | Override this key only in the named session | Non-empty string, except reserved ASK | Non-empty string |
| revoke | Clear global preference and all temporary exceptions for this key | null | null |
| note | Record information without changing preferences | Non-empty string | null |

A temporary override has precedence over the global value within its own session. The most recent override for the same key and session wins. Unrelated keys cannot modify one another. If no applicable preference exists, the answer is `ASK`.

Clearing temporary overrides on a new global set is an explicit simplification of this prototype. It is not a universal product rule. Temporary overrides remain associated with a session ID; the initial schema has no expiry clock or session-end event.

Checkpoints contain `id`, `as_of_step`, `key`, `session_id`, `expected`. IDs are unique within each scenario's checkpoints. `as_of_step` is an integer from 1 through the final event step; queries before the first event are not supported in this initial schema. Querying an unset key is allowed and can be labeled `ASK`.

The reference answers are explicitly authored from the agreed scenario table, not calculated from policy outputs. Validation checks structure, not whether an expected answer is semantically correct. Human review remains necessary.

## Input isolation for future policies

The evaluator must construct an event prefix ending at `as_of_step` and pass only that prefix, the query key, and session ID to a policy. It must not pass checkpoints, expected labels, scenario category/ID, or future events. `Event` contains no answer field. Policy execution is not implemented yet; this boundary must be enforced when the runner is added.

## Planned comparison

`naive_last_value` selects the latest set/temporary value for the queried key, ignoring session scope and revocation. `scoped_state` applies the rules above. These are local reference programs, with no language model involved. Matching labels on these synthetic fixtures demonstrates rule conformance, not general AI capability.
