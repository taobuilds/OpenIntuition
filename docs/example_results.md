# OpenIntuition results

Exact matches against authored labels. These synthetic cases test event rules; they do not measure language-model capability. Checkpoints within a scenario are related.

| Policy | Correct checkpoints | Accuracy | Fully correct scenarios |
| --- | ---: | ---: | ---: |
| naive_last_value | 19/24 | 79.2% | 4/8 |
| scoped_state | 24/24 | 100.0% | 8/8 |

## By category

| Policy | Category | Correct checkpoints |
| --- | --- | ---: |
| naive_last_value | distractor | 6/6 |
| naive_last_value | revoke | 3/6 |
| naive_last_value | temporary | 4/6 |
| naive_last_value | update | 6/6 |
| scoped_state | distractor | 6/6 |
| scoped_state | revoke | 6/6 |
| scoped_state | temporary | 6/6 |
| scoped_state | update | 6/6 |

## Mismatches

| Policy | Scenario | Checkpoint | Step | Key | Session | Expected | Predicted |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| naive_last_value | temporary_01 | q3 | 3 | theme | S2 | dark | light |
| naive_last_value | temporary_02 | q3 | 3 | language | S1 | en | zh |
| naive_last_value | revoke_01 | q2 | 2 | theme | S1 | ASK | dark |
| naive_last_value | revoke_01 | q3 | 3 | theme | S2 | ASK | dark |
| naive_last_value | revoke_02 | q2 | 2 | format | S1 | ASK | bullets |
