# Adjudication packet

Use only after A and B independently submit. Blank forms are not review evidence.
The coordinator archives both submitted records with hashes before comparison.
Use the existing command for each paired case:

```bash
python -m qrefactorbench compare-annotations /path/to/A/annotation.json /path/to/B/annotation.json --json
```

Save the comparison output; it contains field differences, not an agreement score.
The raw tool distinguishes null from [] and compares ordering literally. Review
semantically equivalent spans/text manually instead of treating every textual
difference as a scientific disagreement.

Record submitted artifact paths/hashes, expert identity, disagreements, evidence,
resolutions and remaining uncertainty in adjudication.json. Copy unchanged source
and public task facts from the matching packet if needed. No draft curator label is
an authority; you may consult it only after independent submissions are preserved.

Write a separate adjudicated case.json from the agreed findings, preserving the
original DRAFT material and case ID with an incremented case version. Add the two
independent records, comparison and resolution artifacts to review metadata using
the existing case schema. Promote only when all schema and scientific conditions
are met; unresolved suitability/support may require leaving the case DRAFT.
Do not mark a case FROZEN or invent oracle thresholds merely to satisfy validation.

Intent recognition and contract applicability of baseline responses require human
semantic judgments. Record these in the failure-analysis form after reference
adjudication, retaining raw predictions and model-run metadata. This is a proposed
human workflow, not an implemented automatic label merger.
