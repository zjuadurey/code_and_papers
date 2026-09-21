"""English CA6000 report and eight-slide PPTX, generated from measured SAT results."""
from html import escape
import json
from pathlib import Path
import re

from PIL import Image
import pandas as pd

from coursework.build_slides import Slide, write_pptx, BG, CYAN, AMBER, MUTED
from .data import HERE

RESULTS=HERE/"results"
OUT=HERE/"deliverables"
LOGO=HERE/"assets"/"ntu-logo.png"


def apply_white_ntu_theme(pages):
    """Restyle only this deck; retain university artwork and its aspect ratio."""
    palette={BG:"FFFFFF", "18263C":"F2F4F8", "F1F6FF":"20233D",
             MUTED:"566176", CYAN:"282758", AMBER:"9B2444",
             "263B54":"E5E9F2", "304057":"D5DAE5"}
    with Image.open(LOGO) as logo:
        ratio=logo.width/logo.height
    for p in pages:
        for obj in p.objects:
            if "color" in obj:
                obj["color"]=palette.get(obj["color"],obj["color"])
            if obj["kind"]=="rect" and obj["y"]==850:
                obj.update(x=245,y=840,w=1290)
            if obj["kind"]=="text" and obj["y"]==866:
                obj.update(x=245,w=1140,lines=["CA6000 | Boolean Satisfiability Prediction | Coursework"])
        p.rect(65,825,160,65,"282758")
        width=140;height=round(width/ratio)
        p.image(75,825+(65-height)//2,width,height,LOGO)
        if p.number==1:
            p.rect(1175,35,360,135,"282758")
            width=320;height=round(width/ratio)
            p.image(1195,35+(135-height)//2,width,height,LOGO)


def page(title,section,n):
    return Slide(title,section,n,brand="CA6000 / SAT STUDY",
                 footer="Synthetic small-CNF study | Exact labels, approximate predictions | Not quantumization classification")


def deck(m):
    pages=[]
    p=page("","CASE STUDY",1);pages.append(p)
    p.text(65,152,950,215,"Learning to Predict\nBoolean Satisfiability",64,CYAN)
    p.text(65,402,900,120,"A QRefactorBench-Inspired\nNeural Network Case Study",40)
    p.text(65,565,900,115,"Generate → inspect → clean → train → evaluate\nAn auditable workflow for CA6000",28,MUTED)
    p.text(65,745,900,60,"Name / Student ID / Partner: complete before submission",23)
    p.card(1050,210,485,175,"3,000 instances","30 features; exact SAT labels.")
    p.card(1050,425,485,175,"A real trained MLP","PyTorch weights and history.")
    p.card(1050,640,485,155,"Reproducible code","No API key or QPU required.",AMBER)

    p=page("From a research case to a dataset","DATA SOURCE",2);pages.append(p)
    p.card(65,205,720,380,"Existing classical program","pilot-001: enumerate assignments\nand return whether all clauses\ncan be satisfied.\n\nLabels come from exhaustive\nevaluation of the original code.")
    p.card(815,205,720,380,"Independent input instances","4–5 variables; 2-CNF, 3-CNF\nand mixed formulas.\nRandom clauses, no planted labels.\n\n3,000 accepted canonical groups;\n1,677 UNSAT / 1,323 SAT.")
    p.text(65,630,1470,105,"Remove duplicates under literal/clause order and all variable renamings.\nSave the generator seed, source hash, formulas and labels.",31,CYAN)
    p.text(65,763,1470,60,"Coursework data are separate from DRAFT benchmark cases and quantum-suitability labels.",25,MUTED)

    p=page("Make data quality visible and reproducible","CLEANING",3);pages.append(p)
    rows=[("Issue in training copy","Detected","Pandas repair"),("Missing feature cells","8","Training-median imputation"),
          ("Text / infinity / negative counts","3 / 1 / 2","to_numeric + replace + mask"),
          ("Duplicates / invalid label","4 / 1 rows","drop_duplicates + label filter"),
          ("Impossible literal total","1: 100,000,000","Domain check → NaN → impute")]
    for i,(a,b,c) in enumerate(rows):
        y=205+i*95;p.rect(65,y,1470,87,"263B54" if i==0 else "18263C")
        p.text(87,y+26,590,40,a,25,CYAN if i==0 else "F1F6FF")
        p.text(697,y+26,265,40,b,24);p.text(990,y+26,520,40,c,24)
    p.text(65,719,1470,95,"Errors are intentionally injected only into the training copy.\n1,799 clean rows; 15 imputed cells. Raw, validation and test records stay intact.",28,AMBER)

    p=page("Explore class balance and formula structure","DATA ANALYSIS",4);pages.append(p)
    p.image(65,203,720,420,RESULTS/"class_balance.png")
    p.image(815,203,720,420,RESULTS/"density_distribution.png")
    p.text(65,650,1470,43,"Cleaned training statistics (all 30 features are available in CSV)",28,CYAN)
    stats=pd.read_csv(RESULTS/"training_statistics.csv",index_col=0)
    for i,col in enumerate(["n_clauses","clause_variable_ratio","total_literals"]):
        row=stats.loc[col]
        p.text(65,707+i*39,1470,38,f"{col:24s} mean={row['mean']:.3f}   median={row['50%']:.3f}   variance={row['variance']:.3f}",23,mono=True)

    p=page("Learn from training data; reserve the test set","MODEL & PROTOCOL",5);pages.append(p)
    for x,title,body in [(65,"Train: 1,799","Fit medians, means and scales.\nLearn network parameters."),(560,"Validation: 600","Select the checkpoint using\nvalidation BCE loss only."),(1055,"Test: 601","Evaluate after both models\nand threshold are fixed.")]:p.card(x,205,480,223,title,body)
    p.text(65,483,1470,67,"MLP: 30 → 64 ReLU → 32 ReLU → 1 logit",43,CYAN)
    p.text(65,573,1470,107,"4,097 parameters · BCEWithLogitsLoss · Adam · sigmoid threshold = 0.5\nCompare with majority class and a separately trained linear classifier.",29)
    p.text(65,724,1470,89,"Features use formula statistics only — no solver output, labels or runtime.\nCanonical groups are disjoint; ID and formula hash are never model inputs.",27,MUTED)

    p=page("The network was actually trained locally","TRAINING",6);pages.append(p)
    p.image(65,214,965,535,RESULTS/"training_curve.png")
    p.card(1060,214,475,250,"Fixed configuration","Adam lr = 0.001\nBatch size = 64\nWeight decay = 0.0001")
    p.card(1060,495,475,290,"Recorded run",f"Seed = 42; CPU\n{m['epochs_run']} epochs executed\nBest checkpoint: epoch {m['best_epoch']}\nEarly-stop patience = 25",AMBER)
    p.text(65,785,990,39,"Save weights, per-epoch losses, preprocessing and split group IDs.",25,MUTED)

    p=page("Held-out results: useful, but still fallible","EVALUATION",7);pages.append(p)
    p.image(65,205,700,570,RESULTS/"confusion_matrix.png")
    p.rect(805,205,730,175);p.text(835,222,670,90,f"{m['mlp']['test']['accuracy']:.2%}",70,CYAN)
    p.text(835,322,660,40,"MLP test accuracy · 551 / 601 correct",27)
    p.text(830,420,700,183,f"Linear baseline      {m['linear']['test']['accuracy']:.2%}\nMajority baseline   {m['majority_baseline_accuracy']:.2%}\nSAT precision        {m['mlp']['test']['precision_sat']:.2%}\nSAT recall              {m['mlp']['test']['recall_sat']:.2%}",30)
    p.text(830,641,700,158,"22 false SAT / 28 false UNSAT.\nFeature-distinct subset: 91.62% (597).\nOne split; no significance claim.\nExact solving is still the verifier.",27,AMBER)

    p=page("What was built, and what was learned","DELIVERY & REFLECTION",8);pages.append(p)
    p.card(65,205,720,373,"Reproducible deliverables","Generator + immutable dataset\nPandas cleaning + EDA\nPyTorch training + saved inference\nInteractive prediction / exact check\nReport, English slides and tests")
    p.card(815,205,720,373,"AI assistance and limits","Codex helped draft and debug code,\ntests, plots and documentation.\n\nSmall synthetic distribution; lossy\nfeatures; no solver replacement\nor quantum-advantage claim.",AMBER)
    p.text(65,630,1470,85,"bash scripts/run_sat_app.sh",40,CYAN,mono=True)
    p.text(65,718,1470,81,"Demo: http://127.0.0.1:8766\nA trained neural prediction is checked against exact classical behavior.",30)
    apply_white_ntu_theme(pages)
    return pages


def make_report(m):
    stat=pd.read_csv(RESULTS/"training_statistics.csv",index_col=0)
    table="| Feature | Mean | Median | Sample variance |\n|---|---:|---:|---:|\n"
    for col in ["n_variables","n_clauses","clause_variable_ratio","total_literals","positive_literal_fraction"]:
        r=stat.loc[col];table+=f"| {col} | {r['mean']:.5f} | {r['50%']:.5f} | {r['variance']:.5f} |\n"
    sections=[("1. Use case and relationship to QRefactorBench", """This CA6000 assignment studies **neural prediction of Boolean satisfiability**, using a program already present in the author's QRefactorBench project. Given a Boolean formula in conjunctive normal form (CNF), the model predicts whether at least one assignment satisfies every clause. A clause is an OR of signed literals; the whole formula is an AND of clauses. Positive k denotes variable x_k; negative k denotes its negation.

The source program is `cases/pilot/pilot-001/program.py`. Its `has_assignment` function exhaustively enumerates assignments and returns an exact Boolean result. The course task learns an approximate predictor for this behavior. It does **not** predict whether a program is quantumizable, practically worth quantumizing, or semantically safe to migrate. Those scientific benchmark labels remain DRAFT and are not training targets.

The assignment deliverables include runnable code, a dataset, cleaning/EDA artifacts, actual neural-network training, a written report, and an eight-slide English presentation. Name / student ID / partner information must be completed before submission."""),
    ("2. Dataset acquisition and exact labels", """The dataset is self-generated, not downloaded from Kaggle or claimed to be a mined real-world benchmark. `data.py` samples 3,000 distinct small CNF instances with a fixed NumPy generator seed of 2026. It samples 4 or 5 variables and one of three generator modes: 2-CNF, 3-CNF or mixed clauses. Clause counts are uniform from n through min(7*n, the number of possible distinct clauses). Clauses are sampled without replacement; a variable occurs at most once inside a clause and every declared variable must appear somewhere in the formula. No satisfying assignment is planted, no contradictory gadget is deliberately added, and no class-balancing filter examines the label.

Labels are computed by executing the original exhaustive program. A second, independently expressed Boolean evaluator checks all 3,000 saved labels in the tests. At most 32 assignments are needed per formula, so exact labeling is practical here. This establishes SAT/UNSAT labels for the saved inputs, **not expert quantum-migration ground truth**.

The generator sorts literals and clauses and enumerates all variable permutations (up to 5!) to obtain a canonical representation. It rejects repeats of this representation before any train/test split. This handles variable renaming and literal/clause order. It does not eliminate all logically equivalent formulas or all polarity-inversion symmetries. There were 3,101 generation attempts; attempts failing variable coverage or canonical uniqueness were rejected, leaving 3,000 groups. All accepted groups have distinct hashes.

Data are imported with `pd.read_csv('dataset/instances.csv')`. Each row stores an instance ID, canonical group hash, generator mode, variable count, JSON formula, 30 numerical structural features and the exact satisfiability label. Provenance records the generator/source/dataset SHA-256 hashes and parameters. The observed classes are **1,677 UNSAT and 1,323 SAT**; the imbalance was not forced.

The repository currently has no selected open-source license (UNLICENSED / NOASSERTION). This is a local course submission package, not a public benchmark release. No external dataset provenance or license is invented."""),
    ("3. Error checking and cleaning", """The original numeric audit found zero missing feature cells, duplicate canonical groups, invalid labels, nonnumeric cells, infinite values, negative count-like values or impossible literal totals. The original dataset is preserved unchanged. The source code and tests additionally establish valid formulas and exact labels.

As explicitly permitted by the assignment, teaching errors are injected **only into a training copy after splitting**: 8 missing cells, 3 text-valued numeric cells, 2 negative counts, 1 infinity, 1 impossible literal total of 100,000,000, 4 duplicated rows and 1 extra invalid-label row. `error_injection_log.json` records the edits; `training_dirty.csv` retains the corrupted copy. Validation and test rows are not corrupted.

Pandas cleaning applies `drop_duplicates('group_id')`, filters labels to {0, 1}, uses `pd.to_numeric(errors='coerce')`, replaces infinities with NaN and masks negative count-like values. Signed polarity-balance features are allowed to be negative and are not incorrectly removed. Under the declared generator there can be no more than 35 clauses and 3 literals per clause, so a total above 105 is invalid, not merely statistically unusual. This injected impossible value is changed to NaN. Valid extreme observations are not automatically discarded.

All missing/invalid cells are imputed with medians fitted **only on the training subset**. After repair there are 1,799 training records, no missing/invalid numeric cells, and **15 imputed feature cells**. A few derived-feature consistency relationships may be weakened by independent median imputation; this is a transparent pedagogical repair choice rather than reconstructing values from the clean original. The untouched formulas and source data remain available for review.

Standardization also fits only training data: x_scaled = (x - mean_train) / std_train. Zero standard deviations are replaced with 1. No preprocessing statistics are fitted on validation or test samples."""),
    ("4. Elementary analysis and features", f"""UNSAT constitutes {1677/3000:.2%} and SAT {1323/3000:.2%} of the original data. `raw_statistics.csv` contains all 30-feature original statistics, while `training_statistics.csv` describes the cleaned training data. Mean, median and sample variance (ddof=1) are reported below. The scaling transform's population standard deviation (ddof=0) is a separate statistic.

{table}
![Original class distribution](../results/class_balance.png)

![Training-only clause density distribution](../results/density_distribution.png)

The 30 inputs summarize variable/clause counts, clause density and widths, positive-literal proportion, occurrence statistics, signed polarity balance, variable-pair co-occurrence, variable degrees and mean clause variable overlap. Features are invariant to variable naming. They do not call a SAT solver or include its result, runtime, number of satisfying assignments, ID, formula hash or label. Feature extraction is deterministic syntax analysis, not an LLM call.

These aggregate features deliberately simplify representation and discard information. Different non-isomorphic formulas can share the same feature vector. The audit found 21 repeated feature rows and 4 identical feature vectors shared between train and test; no conflicting labels were observed within repeated-feature groups in this dataset. Therefore canonical formula separation is not the same as completely unique feature-vector separation. This limitation is retained rather than hidden."""),
    ("5. Neural network and training protocol", f"""After label-stratified shuffling with seed 42, the split is **1,799 training / 600 validation / 601 test** (approximately 60/20/20). Canonical group IDs are disjoint and saved. Exact duplicates are removed before splitting; the teaching duplicates are introduced only inside training and then removed. Class stratification uses labels to form the split, not to tune a prediction rule.

The PyTorch MLP is **30 → 64 ReLU → 32 ReLU → 1 logit**, with {m['parameters']:,} trainable parameters. `BCEWithLogitsLoss` provides stable binary training. Sigmoid is used at inference with a threshold of 0.5 fixed before evaluation. Adam uses learning rate 0.001, weight decay 0.0001 and batches of 64.

Two configurations were predeclared: this MLP and a 30 → 1 logistic/linear classifier trained separately. A training-majority baseline is also evaluated. Both trainable models use a maximum of 200 epochs, validation-loss checkpoint selection, early-stop patience 25 and minimum improvement 0.00001. The test set is not used for model, epoch, feature or threshold selection.

The MLP ran for **{m['epochs_run']} epochs**, selecting **epoch {m['best_epoch']}**. The linear model ran for {m['linear_epochs_run']} epochs, selecting epoch {m['linear_best_epoch']}. There was no architecture sweep or retry to obtain a preferred test score. Saved artifacts include weights, both loss histories, preprocessing statistics, split groups and environment metadata.

![Actual MLP loss history](../results/training_curve.png)"""),
    ("6. Prediction evaluation and interpretation", f"""| Model | Test accuracy |
|---|---:|
| Training-majority baseline | {m['majority_baseline_accuracy']:.2%} |
| Linear classifier | {m['linear']['test']['accuracy']:.2%} |
| MLP | {m['mlp']['test']['accuracy']:.2%} |

The MLP correctly predicts **551 of 601** held-out instances. SAT is the positive class. Its precision is **{m['mlp']['test']['precision_sat']:.2%}**, recall **{m['mlp']['test']['recall_sat']:.2%}**, and F1 **{m['mlp']['test']['f1_sat']:.2%}**. Confusion matrix rows are exact [UNSAT, SAT], columns predicted [UNSAT, SAT]: `[[314, 22], [28, 237]]`. The model makes 22 false-SAT and 28 false-UNSAT predictions.

![Held-out confusion matrix](../results/confusion_matrix.png)

The MLP has five more correct predictions than the linear baseline on this split. This small difference is descriptive, not statistical evidence that neural nonlinear modeling is superior. No significance test, multiple-seed study, or cross-distribution evaluation was performed.

After the primary run, a transparent sensitivity analysis excluded the four test rows whose exact feature vectors appeared in training. On the remaining **597** examples, MLP accuracy is **91.62%**. This subset analysis did not retrain the model, change the primary split or replace its reported result; it is recorded in `feature_distinct_sensitivity.json`.

An exact solver is the source of the labels and can decide these small instances correctly; the MLP is not presented as a better solver. No timing comparison or computational/quantum advantage is claimed. The observed neural errors demonstrate why a prediction cannot serve as a satisfiability proof or silently replace an exact program contract."""),
    ("7. Reproduction and interactive demonstration", f"""Use `bash scripts/run_sat_coursework.sh --output /tmp/sat-course-reproduce` from the package root to reproduce training. The command refuses to overwrite an existing output directory. The supplied dataset is reused; regeneration is available via `python -m coursework.sat_case_study.data --output /tmp/sat-course-data`. Inspect hashes and configuration before comparing outputs.

The recorded environment is Python {m['versions']['python']}, PyTorch {m['versions']['torch']}, Pandas {m['versions']['pandas']}, NumPy {m['versions']['numpy']} and Matplotlib {m['versions']['matplotlib']}. It uses a single CPU thread and deterministic PyTorch algorithms. Cross-version/platform bitwise identity is not guaranteed.

Run `python -m pytest -q coursework/sat_case_study/test_study.py` to check canonicalization/invariant features, all 3,000 exact labels using an independent evaluator, group-disjoint splits, cleaning, training-only preprocessing, loaded-model metric reproduction and prediction input validation.

Run `bash scripts/run_sat_app.sh` and open `http://127.0.0.1:8766`. The page loads the trained weights and performs genuine inference on a selected or edited formula, then independently evaluates it with the original classical program. It deliberately includes an observed error example so users can inspect disagreement. Selected examples are from the existing test set, not additional unseen evaluation. Probabilities are uncalibrated model outputs, not guarantees. The interface accepts bounded formula data, not arbitrary executable source code."""),
    ("8. AI assistance, limitations and sources", """Codex was used as an AI coding assistant to draft and debug generation, cleaning, PyTorch training/inference, tests, charts, the demonstration interface and documentation. Actual local commands produced the saved data, weights and metrics; model scores were not generated as prose or manually invented. The student should read, reproduce and understand the submission and accurately describe their own contribution before submitting. No claim is made that all code was manually written by the student or already independently reviewed.

The assignment's primary contribution is a complete, auditable development workflow. Limitations include synthetic input distributions, very small formulas, a lossy feature representation, some feature-vector overlap, one fixed split/seed, and no proven predictive generalization beyond this generator. Median repair can also weaken dependencies between derived features. Larger or real-world SAT datasets, representation comparisons, cross-validation and leakage-aware feature-group splits are potential future work; none are reported as completed experiments here.

Sources and provenance:
1. User-provided CA6000 specification (due 20 September 2026): dataset acquisition, cleaning, elementary analysis, neural-network training/evaluation, report plus code, and disclosure of AI assistance.
2. QRefactorBench local source `cases/pilot/pilot-001/program.py`, functions `satisfies` and `has_assignment`; exact source hash in `dataset/provenance.json`.
3. This submission's `data.py`, `train.py`, `predict.py`, `test_study.py`, and `dataset/provenance.json` define the synthetic dataset and method.
4. Actual artifacts: `results/metrics.json`, `training_history.csv`, `linear_history.csv`, `test_predictions.csv`, `split_groups.json`, audit files and model weights.

The original benchmark cases, DRAFT quantumization labels, schemas, evaluator semantics and completed model experiments remain unchanged. This course study is not a new independent quantumization baseline or a quantum-advantage result.""")]
    (OUT/"CA6000_SAT_REPORT.md").write_text("# CA6000 Assignment Report\n\n# Learning to Predict Boolean Satisfiability\n\n"+"\n\n".join('## '+title+'\n\n'+body for title,body in sections)+"\n")
    def inline(text):
        text=escape(text);text=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',text)
        return re.sub(r'`([^`]+)`',r'<code>\1</code>',text)
    html=[]
    for title,body in sections:
        chunks=[]
        for paragraph in body.split('\n\n'):
            if paragraph.startswith('!['):
                match=re.match(r'!\[(.*?)\]\((.*?)\)',paragraph)
                chunks.append(f'<figure><img src="{match[2]}" alt="{escape(match[1])}"><figcaption>{escape(match[1])}</figcaption></figure>')
            elif paragraph.startswith('|'):
                cells=[]
                for i,row in enumerate(paragraph.splitlines()):
                    if i==1:continue
                    tag='th' if i==0 else 'td';cells.append('<tr>'+''.join(f'<{tag}>{inline(c.strip())}</{tag}>' for c in row.strip('|').split('|'))+'</tr>')
                chunks.append('<table>'+''.join(cells)+'</table>')
            else:chunks.append('<p>'+inline(paragraph).replace('\n','<br>')+'</p>')
        html.append('<section><h2>'+escape(title)+'</h2>'+''.join(chunks)+'</section>')
    style='body{font:11pt/1.55 Arial,sans-serif;color:#182d3e;max-width:850px;margin:40px auto}h1,h2{color:#117b6e}h1{font-size:25pt}h2{font-size:16pt;margin-top:30px}code{font-size:9pt;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%;font-size:10pt}th,td{border:1px solid #cad7dc;padding:7px;text-align:left}th{background:#e7f3f0}figure{text-align:center;break-inside:avoid;margin:18px auto}img{max-width:77%;max-height:280px}figcaption{font-size:9pt;color:#546a79}@page{size:A4;margin:18mm}@media print{body{margin:0;font-size:10pt}h2{break-after:avoid}p{orphans:3;widows:3}table{break-inside:avoid}}'
    (OUT/"CA6000_SAT_REPORT.html").write_text('<!doctype html><meta charset="utf-8"><title>CA6000 SAT Report</title><style>'+style+'</style><h1>CA6000 Assignment Report</h1><h2>Learning to Predict Boolean Satisfiability</h2><p>A QRefactorBench-Inspired Case Study<br>Name / Student ID / Partner: complete before submission.</p>'+''.join(html))


def main():
    OUT.mkdir(exist_ok=True);m=json.loads((RESULTS/"metrics.json").read_text())
    pages=deck(m);images=[]
    for i,p in enumerate(pages,1):
        im=p.preview();im.save(OUT/f'slide-{i:02}.png');images.append(im)
    images[0].save(OUT/'CA6000_SAT_PRESENTATION.pdf',save_all=True,append_images=images[1:],resolution=120)
    write_pptx(pages,OUT/'CA6000_SAT_PRESENTATION.pptx')
    sheet=Image.new('RGB',(1600,900),'#FFFFFF')
    for i,im in enumerate(images):sheet.paste(im.resize((400,225)),((i%4)*400,(i//4)*450+100))
    sheet.save(OUT/'overview.png');make_report(m)
    print('Created 8 English slides: PPTX, PDF, PNG previews; English report: Markdown + HTML')


if __name__=='__main__':main()
