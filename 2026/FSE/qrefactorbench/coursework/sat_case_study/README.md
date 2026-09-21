# CA6000 — Learning to Predict Boolean Satisfiability

**Selected submission:** this SAT study, not the earlier quantum-only demo or the
unused medical-data alternative. It uses an existing QRefactorBench classical
program as an exact labeling oracle and trains a real PyTorch neural network.
The report, eight-slide presentation, plots and interactive interface are in English.
The presentation uses a white background with navy text and the NTU Singapore logo
on its cover and footers. The unchanged university artwork comes from the
[official NTU student-organisation site](https://soms.ntu.edu.sg/home_login);
[asset provenance](assets/logo_source.json) records the URL and hash. The mark is
not covered by the software license. The previous navy slides are retained locally
in `deliverables/archive/navy_before_ntu_white.zip` (excluded from the submission).

## Open these first

- [English presentation, 8 slides](deliverables/CA6000_SAT_PRESENTATION.pptx)
- [Presentation PDF preview](deliverables/CA6000_SAT_PRESENTATION.pdf)
- [English report, 7 PDF pages](deliverables/CA6000_SAT_REPORT.pdf)
- [Editable report source](deliverables/CA6000_SAT_REPORT.md)
- [Speaker notes and demonstration script](SPEAKER_NOTES.md)

Before submission, fill in your name, student ID and partner information. Read the
code and reproduce the steps you intend to explain. AI coding assistance is disclosed
in the report; the report does not misrepresent generated code as independently
handwritten student work.

## Run the visual demonstration

From the package/repository root:

```bash
bash scripts/run_sat_app.sh
```

Open **http://127.0.0.1:8766**. Choose SAT, UNSAT, or an observed model error; click
**Predict + verify**. The saved MLP actually runs, then the original exact solver
checks the formula. The page accepts bounded formula data, never executable code.
There is no API key, live LLM invocation or quantum-hardware dependency.

The shell wrapper uses the existing `palqo` environment if available. Alternatively,
use a Python environment with the listed dependencies:

```bash
python -m coursework.sat_case_study.app
```

## Reproduce the neural-network experiment

```bash
# Reuse supplied, fixed data; choose a NEW result directory.
bash scripts/run_sat_coursework.sh --output /tmp/sat-course-reproduce

# Equivalent portable command, including Windows Python:
python -m coursework.sat_case_study.train --output ./my_sat_results

# Regenerate data without overwriting the submitted dataset:
python -m coursework.sat_case_study.data --output ./my_sat_dataset

# Run the focused checks:
python -m pytest -q coursework/sat_case_study/test_study.py
```

Python packages are listed in `requirements.txt` in the submission ZIP (also
`coursework/sat_case_study/requirements.txt` in the repository). Training was tested
with Python 3.10.21 on CPU. Dependencies were already installed locally; this task
did not install packages. CPU execution works with the recorded CUDA-enabled
PyTorch build and does not need a GPU. The shell scripts allow `CA6000_PYTHON` to
select another existing interpreter.

## Actual result, not a target score

| Item | Recorded value |
|---|---:|
| Synthetic instances / canonical groups | 3,000 / 3,000 |
| UNSAT / SAT labels | 1,677 / 1,323 |
| Train / validation / test | 1,799 / 600 / 601 |
| MLP architecture | 30 → 64 → 32 → 1 |
| Parameters | 4,097 |
| MLP test accuracy | 91.68% (551 / 601) |
| Linear test accuracy | 90.85% |
| Majority test accuracy | 55.91% |
| SAT precision / recall / F1 | 91.51% / 89.43% / 90.46% |
| MLP epochs / selected checkpoint | 44 / 19 |

There were no test-score-driven retries or architecture changes. A post-hoc audit
found four test rows sharing exact feature vectors with training; excluding them
gives 91.62% on 597 rows without retraining. Both primary and sensitivity results
are retained. Canonicalization prevents variable-renaming/order duplicates; it does
not claim to detect every logically equivalent formula. All 3,000 labels were
checked by a second Boolean evaluator.

## What the files do

| File | Role |
|---|---|
| `data.py` | Sample formulas, canonicalize, compute 30 features, label with original solver |
| `train.py` | Stratify, inject documented training errors, clean, train MLP/linear baseline, evaluate |
| `predict.py` | Load saved preprocessing/weights; compare predictions with exact behavior |
| `app.py`, `index.html` | Small local English interactive demonstration |
| `test_study.py` | Label, isolation, cleaning, inference and reproduction checks |
| `dataset/` | Preserved instances and provenance/hashes |
| `results/` | Dirty/clean data, training history, weights, predictions, metrics and figures |
| `build_deliverables.py` | Build English report and editable PowerPoint from real results |
| `deliverables/` | PPTX, PDF, report and slide previews |

Presentation regeneration uses Pillow plus the small existing OOXML helper
`coursework/build_slides.py`. It uses the fonts configured in that helper; adjust
font paths on another OS if rebuilding slides. Existing PPTX/PDF files can be opened
without Python. The report PDF was rendered from HTML in local Chromium.

## Boundaries and verification

- The target is **SAT/UNSAT**, not quantum eligibility or migration suitability.
- The data are **synthetic instances derived from one program**, not 3,000 new
  scientific benchmark programs. No original labels/schemas/evaluators were changed.
- An exact solver already handles these small formulas. The model is fallible and
  is not claimed to replace it, outperform it, or provide quantum advantage.
- AI assistance and the dataset's generation procedure are explicitly disclosed.
- The source repository has not selected an open-source license. `LICENSE` is
  preserved in the private submission package; no redistribution rights are invented.
- Runtime evidence includes six focused passing tests, browser checks, independently
  verified labels, saved-model metric agreement, and source/artifact hash checks.
- The submission was extracted outside the repository with `PYTHONPATH` removed;
  retraining reproduced the full metrics JSON and test-prediction CSV exactly.
  All six study tests also passed in that extracted copy. The final archive adds
  these validation records to the same tested implementation/data.
- The PPTX package and previews are validated separately. An attempted automatic
  PowerPoint COM render was blocked by the local Windows script execution policy;
  no security policy was changed. The supplied slide PDF is an independently rendered
  visual preview, not a claim of successful native PowerPoint rendering.

Assessment mapping and provenance: [CA6000 requirements](../CA6000_REQUIREMENTS.md),
`dataset/provenance.json`, and the English report. See `results/validation.json`
for the final mechanical validation record.
