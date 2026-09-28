# English speaker notes — approximately 6–8 minutes

## Slide 1 — Learning to Predict Boolean Satisfiability

“My case study comes from my QRefactorBench project. For this course I chose one
classical program and built a supervised-learning workflow around its inputs and
outputs. The goal is not to train a quantum computer or to decide which programs
should be quantumized. The goal is to predict whether a small Boolean formula is
satisfiable, and to evaluate that prediction honestly against an exact program.”

## Slide 2 — Dataset source

“Each sample is a different formula, not a copy of the source program. I used
AI-assisted code to generate 3,000 formulas with four or five variables. The
existing exhaustive solver computes every label. A second Boolean evaluator checks
the labels. Variable renaming and clause/literal ordering are canonicalized before
splitting, so those simple transformations do not create train/test duplicates.
The generator does not plant satisfying assignments or force balanced classes.”

## Slide 3 — Data cleaning

“The original data passed the numeric checks. The assignment permits intentional
errors, so I injected them only into a training copy. The report records missing
values, text in numeric columns, invalid negative counts, infinity, duplicate rows
and an invalid label. A literal count of one hundred million is impossible under
the generator's declared bounds. Pandas detects these issues and medians from the
training set fill the resulting missing cells. Original data remain unchanged.”

## Slide 4 — Elementary analysis

“This chart shows the observed class imbalance. The second plot uses only training
data and illustrates the relationship between clause density and the labels.
The CSV includes mean, median and sample variance for every feature. These patterns
help explain why a structural-statistics predictor can be useful, but a histogram
does not prove that every dense formula is unsatisfiable.”

## Slide 5 — Model and protocol

“There are 30 numeric features and no solver outputs or labels among the inputs.
The network has two ReLU hidden layers with 64 and 32 units. I also evaluate a
majority baseline and a linear classifier. Preprocessing uses training data only;
validation loss selects the epoch. The test set is reserved until the model and
threshold are fixed. The neural model predicts a probability, not a logical proof.”

## Slide 6 — Actual training

“This is the saved loss history from the real CPU run, not an illustrative curve.
The MLP trained for 44 epochs and restored the checkpoint from epoch 19. Seed,
batch size, optimizer and stopping rule were fixed. I saved the model weights,
preprocessing values, split IDs and per-epoch losses so the process can be rerun.”

## Slide 7 — Evaluation

“The MLP correctly predicted 551 of 601 held-out formulas, or 91.68 percent. The
linear baseline achieved 90.85 percent, so the difference is only five predictions
and does not justify a significance claim. The neural model still makes 50 errors.
Four held-out formulas share their feature vectors with training; removing those
rows gives 91.62 percent without retraining. This is a limited synthetic study.”

## Slide 8 — Deliverables, AI use and live demonstration

“Codex helped draft and debug code, tests, plots and documentation. All metrics come
from actual saved execution artifacts. The delivered code includes generation,
cleaning, training, prediction and an interactive demo. I will now show the saved
neural network making a prediction and the original exact program checking it.”

### Live demonstration — about one minute

1. Run `bash scripts/run_sat_app.sh`; open `http://127.0.0.1:8766`.
2. Choose **SAT example**, click **Predict + verify**, explain model versus exact output.
3. Choose **An observed model error**, click again, and point out **MISMATCH**.
4. Explain: “This example was selected from the existing test set to show a real
   failure. It is not a new test or evidence that the model always fails.”
5. End with: “Approximate prediction can be studied, but it must not silently replace
   the original exact software behavior.”

## Likely questions

**Why synthetic data?** They come from a program in my project, with transparent
generation and exact labels. The trade-off is limited realism and distribution scope.

**Why use a neural network when brute force is easy here?** It is a controlled
learning exercise, not a claim that the model is the preferred small-instance solver.

**Does it classify quantumizable programs?** No. The labels are mathematical
SAT/UNSAT outcomes. Quantum migration labels remain a separate research question.

**Can the model prove UNSAT?** No. Its decisions can be wrong; the original solver
provides the exact comparison for this bounded domain.

**What should be improved next?** Richer representations, broader data, and evaluation
across generators or seeds; those are future work, not results already obtained.

Before speaking, read the code and adapt these notes to accurately reflect your own
understanding and participation. Fill in the student information on slide 1/report.
