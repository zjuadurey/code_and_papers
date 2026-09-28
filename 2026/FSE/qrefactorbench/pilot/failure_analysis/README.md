# Open-coded failure analysis

Copy observation_template.json once per observation; multiple observations may
belong to the same case. task may describe T1, T2 or T3; open_code is free text,
not an enumerated taxonomy. Include source lines/prediction excerpts and retain
alternative explanations and reference uncertainty. Null human judgments mean
unreviewed, never incorrect.

Possible observations to consider (examples only, not required categories):

- Mistook a computational hotspot for a supported quantum opportunity.
- Recovered the intent but selected the wrong migration family.
- Ignored the stipulated encoding or data-loading assumption.
- Quantumized a provisionally negative case without addressing its effects.
- Selected a region broader than needed.
- Recognized structural eligibility but conflated it with practical suitability.

Also record correct abstentions, ambiguous reference annotations, invalid JSON,
missing responses and cases with no observed failure. Do not force every response
into a failure label. Separate an annotation disagreement from a model error.
Review observations only after independent reference annotation is preserved;
record any later reference revision explicitly. Derive a taxonomy from repeated
evidence later, without turning these suggestions into measured findings.
