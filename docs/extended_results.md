# OpenIntuition results

Exact matches against authored labels. These synthetic cases test event rules; they do not measure language-model capability. Checkpoints within a scenario are related.

| Policy | Correct checkpoints | Accuracy | Fully correct scenarios |
| --- | ---: | ---: | ---: |
| naive_last_value | 54/72 | 75.0% | 10/20 |
| scoped_state | 72/72 | 100.0% | 20/20 |

## By category

| Policy | Category | Correct checkpoints |
| --- | --- | ---: |
| naive_last_value | distractor | 18/18 |
| naive_last_value | revoke | 7/18 |
| naive_last_value | temporary | 11/18 |
| naive_last_value | update | 18/18 |
| scoped_state | distractor | 18/18 |
| scoped_state | revoke | 18/18 |
| scoped_state | temporary | 18/18 |
| scoped_state | update | 18/18 |

## Mismatches

| Policy | Scenario | Checkpoint | Step | Key | Session | Expected | Predicted |
| --- | --- | --- | ---: | --- | --- | --- | --- |
| naive_last_value | temporary_01 | q3 | 3 | theme | S2 | dark | light |
| naive_last_value | temporary_02 | q3 | 3 | language | S1 | en | zh |
| naive_last_value | revoke_01 | q2 | 2 | theme | S1 | ASK | dark |
| naive_last_value | revoke_01 | q3 | 3 | theme | S2 | ASK | dark |
| naive_last_value | revoke_02 | q2 | 2 | format | S1 | ASK | bullets |
| naive_last_value | temporary_03 | q2 | 2 | theme | S2 | ASK | light |
| naive_last_value | temporary_03 | q4 | 4 | theme | S1 | dark | sepia |
| naive_last_value | temporary_04 | q4 | 5 | language | S3 | en | de |
| naive_last_value | temporary_05 | q1 | 3 | format | S1 | table | paragraphs |
| naive_last_value | temporary_05 | q4 | 4 | format | meeting | bullets | outline |
| naive_last_value | revoke_03 | q1 | 3 | theme | S1 | light | sepia |
| naive_last_value | revoke_03 | q2 | 4 | theme | S1 | ASK | sepia |
| naive_last_value | revoke_03 | q3 | 4 | theme | S2 | ASK | sepia |
| naive_last_value | revoke_03 | q4 | 5 | theme | S3 | ASK | sepia |
| naive_last_value | revoke_04 | q1 | 3 | language | S1 | ASK | en |
| naive_last_value | revoke_05 | q1 | 2 | theme | S1 | ASK | dark |
| naive_last_value | revoke_05 | q3 | 4 | theme | S1 | ASK | light |
| naive_last_value | revoke_05 | q4 | 5 | theme | S2 | ASK | light |
