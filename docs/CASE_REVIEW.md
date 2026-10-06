# Extended case review

`data/extended_scenarios.jsonl` contains the original eight pilot sequences plus twelve longer cases. The files overlap: do not count the pilot and extended suite as separate evaluation samples. Extended version: `extended-0.1` (20 scenarios, 72 checkpoints, five scenarios per category).

Expected values below were specified directly from the event rules before running either policy. These remain AI-assisted development fixtures, not independently reviewed or held-out evaluation data. Human review is still a next step.

| Added scenario | Boundary being checked | Expected values in checkpoint order |
| --- | --- | --- |
| update_03 | A global set clears exceptions in two sessions | light, sepia, blue, blue |
| update_04 | Repeated global changes and an intervening note | bullets, table, table, bullets |
| update_05 | Resetting theme leaves a language exception alone | zh, light, sepia, zh |
| temporary_03 | Session overrides without a global value; latest override per session wins | light, ASK, dark, dark |
| temporary_04 | Overrides in two sessions; updating S1 leaves S2 and the global default alone | zh, fr, de, en |
| temporary_05 | Case-sensitive and Unicode session IDs remain distinct | table, paragraphs, outline, bullets |
| revoke_03 | Revocation clears both the global value and all session exceptions | light, ASK, ASK, ASK |
| revoke_04 | Revoking one key, or an unset key, leaves another key alone | ASK, ASK, dark, light |
| revoke_05 | A temporary assignment after revocation does not recreate a global default | ASK, light, ASK, ASK |
| distractor_03 | A note containing ASK or an apparent preference is still a note | dark, dark, dark, dark |
| distractor_04 | Revoking another key cannot alter the queried preference | bullets, bullets, bullets, bullets |
| distractor_05 | Notes and other keys cannot create an unset preference | ASK, ASK, ASK, ASK |

For review, read the events and query session before looking at the label. Derive the answer on paper, then compare with `validate --review`. If the rule is unclear, discuss the rule rather than changing a label to agree with a policy output.

All histories use explicit operations. This suite cannot assess whether natural language was correctly classified as a preference, a quotation, a revocation, or a note.
