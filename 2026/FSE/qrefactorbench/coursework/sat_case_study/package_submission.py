"""Package only the selected coursework and its exact local source dependency."""
import hashlib
import json
from pathlib import Path
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]


def main():
    files=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts
           and p.suffix!='.zip' and 'native_render' not in p.parts]
    files += [ROOT/'coursework/__init__.py',ROOT/'coursework/build_slides.py',
              ROOT/'coursework/CA6000_REQUIREMENTS.md',ROOT/'cases/pilot/pilot-001/program.py',
              ROOT/'scripts/run_sat_coursework.sh',ROOT/'scripts/run_sat_app.sh',ROOT/'LICENSE']
    manifest={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(files)}
    target=HERE/'deliverables/CA6000_SAT_Submission.zip'
    root_readme='''# CA6000 SAT Prediction — Start Here

Selected topic: Learning to Predict Boolean Satisfiability, inspired by QRefactorBench.

1. Slides: coursework/sat_case_study/deliverables/CA6000_SAT_PRESENTATION.pptx
2. Report: coursework/sat_case_study/deliverables/CA6000_SAT_REPORT.pdf
3. Full instructions: coursework/sat_case_study/README.md
4. Speaker notes: coursework/sat_case_study/SPEAKER_NOTES.md

From this extracted directory:

    python -m coursework.sat_case_study.app

Open http://127.0.0.1:8766. Or retrain into a NEW directory:

    python -m coursework.sat_case_study.train --output ./reproduced_results
    python -m pytest -q coursework/sat_case_study/test_study.py

Use an environment with requirements.txt. Dependencies are not installed automatically.
Tested on Python 3.10.21, CPU. Supplied weights/data work offline; no API key or QPU.
Add name/student ID to the report and title slide; read/reproduce the work before submission.
AI coding assistance is disclosed. No claim of solver replacement or quantum advantage.
The original repository license status is preserved in LICENSE; this is not a public release.
'''
    with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED) as archive:
        for p in sorted(files):archive.write(p,'CA6000_SAT_Submission/'+str(p.relative_to(ROOT)))
        archive.writestr('CA6000_SAT_Submission/README.md',root_readme)
        archive.writestr('CA6000_SAT_Submission/requirements.txt',(HERE/'requirements.txt').read_bytes())
        archive.writestr('CA6000_SAT_Submission/MANIFEST.json',json.dumps(manifest,indent=2)+'\n')
    print(f'{target}: {len(files)} allowlisted files + README / requirements / manifest')


if __name__=='__main__':main()
