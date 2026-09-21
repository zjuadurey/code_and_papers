# Deliberately incomplete predictions

For CLI mechanics only. The search prediction supplies classical code and names a
contract; neither proves quantumization. The optimization prediction abstains and
therefore deliberately disagrees with its DRAFT positive label. End-to-end success
must never be reported as true for these records. Use --allow-draft explicitly.

These predictions cover only the four original toys, not cases/pilot/. Select the
four IDs explicitly now that the dataset also contains pilot material:

```bash
python -m qrefactorbench evaluate cases examples/draft_predictions.json --allow-draft --json --case-id toy-search-001 --case-id toy-optimization-001 --case-id toy-negative-001 --case-id toy-hard-negative-001
```
