"""Generate the CA6000 report and eight-slide deck from actual saved outputs."""
from html import escape
import json
from pathlib import Path

from PIL import Image
import pandas as pd

from coursework.build_slides import Slide, write_pptx, BG, CYAN, AMBER, MUTED

HERE = Path(__file__).resolve().parent
RESULTS = HERE / "results"
OUT = HERE / "deliverables"


def page(title, section, n):
    return Slide(title, section, n, brand="CA6000", footer="UCI WDBC · PyTorch MLP · 实际运行结果 · 单次固定划分，不代表临床能力")


def deck(m):
    pages=[]
    p=page("", "NEURAL NETWORK CASE STUDY", 1);pages.append(p)
    p.text(65,158,1450,75,"从数据清洗到神经网络预测",62,CYAN)
    p.text(65,267,920,176,"乳腺癌诊断数据的\n分类用例研究",65)
    p.text(65,498,880,145,"公开数据 → 错误检查 → 清洗与统计\n→ PyTorch MLP → 独立测试集评估",32,MUTED)
    p.text(65,724,900,80,"CA6000 · AI Programming Assignment\n提交前补充姓名 / 学号 / 组员信息",26)
    p.card(1040,280,495,180,"569 个样本", "30 个数值特征，二分类。")
    p.card(1040,490,495,180,"实际训练的神经网络", "1,537 个参数；CPU 可复现。")

    p=page("数据来源与任务定义", "DATASET", 2);pages.append(p)
    p.card(65,205,740,352,"UCI · Wisconsin Diagnostic", "官方数据文件：wdbc.data\nPandas read_csv 导入 32 列。\n\nID 只用于追踪，不作为输入；\n30 个特征预测 B / M。")
    p.card(835,205,700,352,"数据来源可核查", "来源：UCI Machine Learning Repository\nDOI: 10.24432/C5DW2B\n许可：CC BY 4.0，保留署名。\n\n原始文件、下载脚本与 hash 均随附。")
    p.text(65,610,1470,125,"B = benign（良性），M = malignant（恶性）\n目标：学习数据分类与评估流程；不构建临床诊断产品。",34,CYAN)
    p.text(65,760,1470,58,"原始检查：569 行；缺失、重复 ID、非法标签、非数字值均为 0。",29,MUTED)

    p=page("数据清洗：把每一类修复留成证据", "CLEANING", 3);pages.append(p)
    rows=[("问题","训练副本检查","修复方法"),("缺失值","8 个","fillna：训练集中位数"),
          ("非数字 / ±∞ / 负值","3 / 1 / 2 个","to_numeric + replace + mask → NaN"),
          ("重复 / 非法标签","4 行 / 1 行","drop_duplicates + 标签过滤"),
          ("人为极端值","1 个：radius = 10⁸","训练集 1%–99% 分位裁剪")]
    for i,(a,b,c) in enumerate(rows):
        y=208+i*94;p.rect(65,y,1470,86, "263B54" if i==0 else "18263C")
        p.text(88,y+24,395,50,a,27,CYAN if i==0 else "F1F6FF")
        p.text(500,y+24,370,50,b,26);p.text(905,y+24,600,50,c,25)
    p.text(65,704,1470,102,"仅污染训练副本；原始、验证和测试数据保持原样。\n清洗后 341 行、0 缺失；共填补 14 个单元格，裁剪 216 个（包含真实尾部值）。",28,AMBER)

    p=page("基础分析：类别分布、特征统计与可视化", "EXPLORATORY ANALYSIS", 4);pages.append(p)
    p.image(65,200,720,420,RESULTS/"class_balance.png")
    p.image(815,200,720,420,RESULTS/"training_scatter.png")
    stats=pd.read_csv(RESULTS/"training_descriptive_statistics.csv",index_col=0)
    p.text(65,649,1470,45,"清洗后的训练集统计（完整版 30 个特征见 CSV）",29,CYAN)
    for i,feature in enumerate(["radius_mean","texture_mean","area_mean"]):
        r=stats.loc[feature]
        p.text(65,707+i*39,1470,38,f"{feature:14s}   mean={r['mean']:.3f}   median={r['50%']:.3f}   variance={r['variance']:.3f}",24,mono=True)

    p=page("建模：先划分数据，再学习预处理参数", "MODEL & SPLIT", 5);pages.append(p)
    for x,title,body in [(65,"训练 · 341 条","中位数、裁剪边界、均值、\n标准差全部只在这里计算。"),(560,"验证 · 113 条","固定模型结构；\n按 validation BCE 选择 epoch。"),(1055,"测试 · 115 条","权重与阈值冻结后评估；\n不参与训练或调参。")]:
        p.card(x,208,480,234,title,body)
    p.text(65,493,1470,68,"MLP：30 → 32 ReLU → 16 ReLU → 1 logit",42,CYAN)
    p.text(65,581,1470,96,"BCEWithLogitsLoss + Adam；预测时 sigmoid，固定阈值 0.5。\nID 与 diagnosis 不进入特征；保存 split IDs，检查三组无交叉。",30)
    p.text(65,725,1470,72,"分层约 60% / 20% / 20% · seed=42 · CPU 确定性执行 · 1,537 个可训练参数",28,MUTED)

    p=page("训练过程：用验证损失选权重，不看测试分数", "TRAINING", 6);pages.append(p)
    p.image(65,215,980,540,RESULTS/"training_curve.png")
    p.card(1075,215,460,254,"固定训练设置", "lr = 0.001\nbatch size = 32\nweight decay = 0.0001")
    p.card(1075,500,460,280,"实际训练记录", f"运行 {m['epochs_run']} 个 epoch\n最佳 epoch = {m['best_epoch']}\npatience = 30\n恢复最佳验证权重。",AMBER)
    p.text(65,783,980,45,"保留 history.csv、model_state.pt 与完整配置。",26,MUTED)

    p=page("测试结果：115 条独立样本，114 条预测正确", "EVALUATION", 7);pages.append(p)
    p.image(65,205,710,570,RESULTS/"confusion_matrix.png")
    p.rect(810,205,725,220);p.text(840,226,665,100,f"{m['test']['accuracy']:.2%}",76,CYAN)
    p.text(840,347,665,55,"Accuracy · 多数类基线 62.61%",29)
    p.text(830,470,700,165,f"Precision (M)   {m['test']['precision_malignant']:.2%}\nRecall (M)         {m['test']['recall_malignant']:.2%}\nF1 (M)                {m['test']['f1_malignant']:.2%}",32)
    p.text(830,679,700,132,"1 个恶性样本被预测成良性。\n单个固定划分的高准确率，\n不能外推为临床可靠性。",30,AMBER)

    p=page("AI 辅助、可复现交付与局限", "REFLECTION", 8);pages.append(p)
    p.card(65,210,730,352,"AI 怎样参与", "Codex 辅助生成训练与清洗代码、\n补充测试、整理图表和报告。\n\n所有指标由本机训练产物计算；\n提交者仍需阅读、复现并能解释代码。")
    p.card(825,210,710,352,"局限与改进", "单一数据集、固定划分和种子；\n分位裁剪可能压缩有意义的极端值。\n\n后续可做交叉验证和清洗消融，\n不能据此声称临床适用。",AMBER)
    p.text(65,613,1470,65,"交付：源码 + 原始数据 + 模型权重 + 结果图表 + 报告 + 8 页 PPT",34,CYAN)
    p.text(65,710,1470,94,"重现：bash scripts/run_ca6000.sh --output /tmp/ca6000-reproduce\n无需调用大模型；运行依赖为已安装的 PyTorch、Pandas、NumPy、Matplotlib。",27)
    return pages


def report(m):
    stats=pd.read_csv(RESULTS/"training_descriptive_statistics.csv",index_col=0)
    table="| Feature | Mean | Median | Sample variance |\n|---|---:|---:|---:|\n"
    for feature in ["radius_mean","texture_mean","perimeter_mean","area_mean","smoothness_mean"]:
        r=stats.loc[feature];table+=f"| {feature} | {r['mean']:.5f} | {r['50%']:.5f} | {r['variance']:.5f} |\n"
    sections=[
    ("1. Use case and dataset source",f"""This CA6000 assignment implements a supervised neural-network classification workflow on the Wisconsin Diagnostic Breast Cancer (WDBC) dataset. The educational target is to predict the recorded diagnosis label from 30 numeric measurements. It is not a clinical diagnostic system. Student name / ID / partner: **complete before submission**.

The official UCI source contains 569 samples, with 357 benign (B) and 212 malignant (M) records. The 30 measurements describe cell-nucleus characteristics derived from images. The downloaded `wdbc.data` contains ID, diagnosis, and 30 numeric columns. `pd.read_csv(..., header=None, names=...)` supplies explicit names. ID is retained for auditing but excluded from predictors; M maps to 1 and B to 0. The dataset license is CC BY 4.0. The raw data and accompanying `wdbc.names` are preserved unchanged, with SHA-256 hashes in `data/provenance.json`.

Citation: Wolberg, W., Mangasarian, O., Street, N., & Street, W. (1993). *Breast Cancer Wisconsin (Diagnostic)* [Dataset]. UCI Machine Learning Repository. https://doi.org/10.24432/C5DW2B.

Official source: https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic
Download: `python -m coursework.ca6000.fetch_data` verifies or retrieves the exact recorded source files; no Kaggle credentials are needed."""),
    ("2. Error checking and controlled cleaning exercise",f"""The original dataset audit found 569 rows, 32 columns, zero missing cells, zero duplicate IDs, zero duplicate rows, zero unknown labels, zero nonnumeric feature cells, zero infinite values and zero negative measurements. No natural source defects are claimed.

To demonstrate the course's permitted cleaning techniques, errors were deliberately introduced **only after splitting, in a training copy**. The validation and test source rows were not corrupted. The copy contains 8 missing cells, 3 nonnumeric cells, 2 negative measurements, 1 infinite measurement, 1 extreme value (`radius_mean = 100000000`), 4 duplicated rows, and 1 extra synthetic row with an invalid label. Each edit is documented in `error_injection_log.json`; the dirty copy is saved separately.

Cleaning uses `drop_duplicates(subset='id')`, known-label filtering, `pd.to_numeric(errors='coerce')`, `replace([inf, -inf], NaN)`, and a negative-value mask. Missing/invalid features are filled using **training medians**. Values are winsorized at **training-only 1st and 99th percentiles**, then standardized using training mean and population standard deviation (`ddof=0`). The same stored transform is applied to validation/test and later predictions.

After cleaning there are {m['split_counts']['train']} training records, no missing/invalid numeric values, {m['imputed_training_cells']} imputed cells, and {m['clipped_training_cells']} clipped cells. Clipped cells include naturally extreme values as well as the injected extreme; **outliers are not automatically data errors**. Winsorization is a transparent coursework modeling choice with a possible loss of useful tail information, not a scientifically established medical rule. Original values are retained for review."""),
    ("3. Elementary analysis and descriptive statistics",f"""Class frequencies are 357 B ({357/569:.2%}) and 212 M ({212/569:.2%}); accuracy therefore needs a majority-class comparison. `raw_descriptive_statistics.csv` provides statistics for all 30 original features. Training-only EDA and cleaned statistics are stored separately; the scatter plot uses only training rows. No feature selection or hyperparameter tuning was performed using test outcomes.

The following values describe the cleaned training partition. Sample variance uses `ddof=1`; median is the 50th percentile. The standardization step's population standard deviation is a separate quantity.

{table}
![Class distribution](../results/class_balance.png)

![Training-only feature plot](../results/training_scatter.png)"""),
    ("4. Model, data split and leakage control",f"""A stratified, seeded split produces {m['split_counts']['train']} training, {m['split_counts']['validation']} validation and {m['split_counts']['test']} test samples, approximately 60/20/20 percent. Every source ID belongs to exactly one partition, and the ID lists are saved. Deduplication prevents duplicated teaching rows from increasing the training sample count. Neither IDs nor target labels appear in the 30 input features. All learned preprocessing statistics are fitted on training only.

The real PyTorch MLP has architecture **30 → 32 ReLU → 16 ReLU → 1 logit**, totaling {m['parameters']:,} trainable parameters. Training uses `BCEWithLogitsLoss`; sigmoid converts logits to probabilities for evaluation. The decision threshold is fixed at 0.5 before examining test scores. Adam uses learning rate 0.001 and weight decay 0.0001, with batch size 32. This is a small nonlinear classifier; a complicated model is unnecessary for the course objective.

One architecture/configuration and one split were used. Validation BCE controls early stopping (maximum 300 epochs, patience 30, minimum improvement 0.00001). The test set is evaluated only after selecting and restoring the best validation checkpoint. Raw full-dataset descriptive summaries are for reporting, not for fitting preprocessing or model selection."""),
    ("5. Actual training and evaluation",f"""CPU training with random seed 42 ran for {m['epochs_run']} epochs. The selected checkpoint was epoch {m['best_epoch']}, determined by validation loss. `history.csv` retains per-epoch training and validation loss; `model_state.pt` stores the selected model. No test-driven reruns, architecture search or threshold adjustment were performed to obtain a desired score.

![Training and validation loss](../results/training_curve.png)

| Measure | Training | Validation | Test |
|---|---:|---:|---:|
| Accuracy | {m['train']['accuracy']:.2%} | {m['validation']['accuracy']:.2%} | {m['test']['accuracy']:.2%} |

On the 115 held-out test examples, 114 predictions were correct. Test accuracy is **{m['test']['accuracy']:.2%}**, malignant-class precision **{m['test']['precision_malignant']:.2%}**, recall **{m['test']['recall_malignant']:.2%}**, and F1 **{m['test']['f1_malignant']:.2%}**. The training-majority predictor (always B) achieves **{m['majority_baseline_accuracy']:.2%}** on the same test set.

Confusion matrix, rows = actual [B, M], columns = predicted [B, M]: `[[72, 0], [1, 42]]`. There is one malignant-to-benign error. This is a single fixed-split result, not statistical evidence of clinical performance. No external cohort, calibration study or clinical validation was undertaken.

![Held-out confusion matrix](../results/confusion_matrix.png)"""),
    ("6. Reproduction, tests and prediction",f"""Run `bash scripts/run_ca6000.sh --output /tmp/ca6000-reproduce` from the code-package root. Choose a new output path; earlier results cannot be silently overwritten. The included data allow offline execution. `fetch_data.py` can independently verify the official download.

The environment used Python {m['versions']['python']}, PyTorch {m['versions']['torch']}, Pandas {m['versions']['pandas']}, NumPy {m['versions']['numpy']} and Matplotlib {m['versions']['matplotlib']}. Training uses one CPU thread and deterministic PyTorch algorithms. Different software/platform versions can still differ numerically; the recorded environment and outputs are the reproduction reference.

`test_pipeline.py` checks split disjointness, preservation of raw inputs, injected-error removal, finite transformed values, unchanged preprocessing on held-out inputs, metric definitions and loaded-model prediction agreement. Run `python -m pytest -q coursework/ca6000/test_pipeline.py`.

For saved-model inference: `python -m coursework.ca6000.predict coursework/ca6000/data/example_features.csv`. This illustrative CSV contains a few already-held-out rows; it is an inference demonstration, **not an additional external test set**. Predictions retain probabilities and class labels without retraining. Use these outputs only for coursework, not patient decisions."""),
    ("7. Use of AI tools and limitations", """OpenAI Codex was used as an AI coding assistant to draft data ingestion, error injection, Pandas cleaning, PyTorch model/training code, validation checks, charts, report text and presentation generation. It also helped identify the initial project mismatch: a quantum-computing demonstration without neural-network training did not satisfy this assignment. The coursework dataset/MLP study is therefore separate from the existing QRefactorBench research artifacts; no research labels were changed.

The reported scores were computed by actual local training/evaluation, not invented by an LLM. AI-generated code was checked by running it and inspecting saved artifacts. The submitting student should independently read and reproduce the work and accurately describe their own contribution; this report does not claim that the student manually wrote every line or has already completed that review.

Limitations include one small public dataset, one seed/split, artificial training-only error injection and a clipping choice that may suppress legitimate tail values. High test accuracy alone does not establish robustness, causal interpretation, generalization to new institutions, or clinical suitability. Future coursework extensions could compare preprocessing choices with cross-validation and assess multiple seeds; these were not performed and are not claimed as results.

The main outcome is an auditable end-to-end workflow: acquire → check → clean → describe → train → evaluate → reproduce."""),
    ("8. References", """1. UCI Machine Learning Repository. Wisconsin Diagnostic Breast Cancer dataset, DOI: https://doi.org/10.24432/C5DW2B. Official dataset page: https://archive.ics.uci.edu/dataset/17/breast+cancer+wisconsin+diagnostic (accessed 2026-09-20). Data license: https://creativecommons.org/licenses/by/4.0/.
2. Dataset documentation included as `data/wdbc.names`; acquisition provenance and SHA-256 values in `data/provenance.json`.
3. Course assignment requirements supplied by the instructor/user, deadline 20 September 2026. The assignment explicitly permits AI coding assistance and intentionally injected data errors.
4. Implementation and evidence in this submission: `train.py`, `predict.py`, `test_pipeline.py`, `results/metrics.json`, `results/history.csv`, `results/test_predictions.csv`, and saved figures. These artifacts substantiate the numerical results.""")]
    header="# CA6000 Assignment Report\n\n# From Data Cleaning to Neural-Network Prediction\n\n**Use case: Wisconsin Diagnostic Breast Cancer classification**\n\n"
    markdown=header+"\n\n".join('## '+title+'\n\n'+body for title,body in sections)+"\n"
    (OUT/"CA6000_REPORT.md").write_text(markdown)
    # Small deterministic Markdown subset conversion for a standalone printable report.
    import re
    def format_text(text):
        text=escape(text)
        text=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',text)
        text=re.sub(r'`([^`]+)`',r'<code>\1</code>',text)
        return text
    html=[]
    for title,body in sections:
        chunks=[]
        for paragraph in body.split('\n\n'):
            if paragraph.startswith('!['):
                match=re.match(r'!\[(.*?)\]\((.*?)\)',paragraph)
                chunks.append(f'<figure><img src="{match[2]}" alt="{escape(match[1])}"><figcaption>{escape(match[1])}</figcaption></figure>')
            elif paragraph.startswith('|'):
                rows=paragraph.splitlines();cells=[]
                for index,row in enumerate(rows):
                    if index==1:continue
                    tag='th' if index==0 else 'td'
                    cells.append('<tr>'+''.join(f'<{tag}>{format_text(cell.strip())}</{tag}>' for cell in row.strip('|').split('|'))+'</tr>')
                chunks.append('<table>'+''.join(cells)+'</table>')
            else:chunks.append('<p>'+format_text(paragraph).replace('\n','<br>')+'</p>')
        html.append('<section><h2>'+escape(title)+'</h2>'+''.join(chunks)+'</section>')
    style='body{font:11pt/1.55 Arial,sans-serif;color:#192b3a;max-width:850px;margin:40px auto}h1,h2{color:#16796b}h1{font-size:26pt}h2{font-size:17pt;margin-top:32px}p{text-align:left}code{font-size:9pt;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%;font-size:10pt}td,th{border:1px solid #cad7dc;padding:7px;text-align:left}th{background:#e8f3f1}figure{margin:20px auto;text-align:center;break-inside:avoid}img{max-width:75%;max-height:290px}figcaption{font-size:9pt;color:#526477}@page{size:A4;margin:18mm} @media print{body{margin:0;font-size:10pt}h2{break-after:avoid}p{orphans:3;widows:3}table{break-inside:avoid}section{break-inside:auto}}'
    (OUT/"CA6000_REPORT.html").write_text('<!doctype html><meta charset="utf-8"><title>CA6000 Report</title><style>'+style+'</style><h1>CA6000 Assignment Report</h1><h2>From Data Cleaning to Neural-Network Prediction</h2><p>Wisconsin Diagnostic Breast Cancer classification<br>Name / Student ID / partner: complete before submission.</p>'+''.join(html))


def main():
    OUT.mkdir(exist_ok=True)
    m=json.loads((RESULTS/"metrics.json").read_text())
    pages=deck(m);previews=[]
    for i,p in enumerate(pages,1):
        im=p.preview();im.save(OUT/f'slide-{i:02}.png');previews.append(im)
    previews[0].save(OUT/'CA6000_PRESENTATION.pdf',save_all=True,append_images=previews[1:],resolution=120)
    write_pptx(pages,OUT/'CA6000_PRESENTATION.pptx')
    sheet=Image.new('RGB',(1600,900),'#'+BG)
    for i,im in enumerate(previews):sheet.paste(im.resize((400,225)),((i%4)*400,(i//4)*450+100))
    sheet.save(OUT/'overview.png')
    report(m)
    print('Created CA6000 report and 8-slide PPTX/PDF from recorded results')


if __name__=='__main__':main()
