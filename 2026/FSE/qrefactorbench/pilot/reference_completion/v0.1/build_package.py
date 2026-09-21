"""Materialize six source-task adaptations and public A/B/C review inputs.

Programs are authored files; this script only writes metadata, examples, attribution
and derived packets. It makes no model call and assigns no scientific truth labels.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PARENT = ROOT / "pilot/source_adaptations/v0.2-where"

SAT = [[1, 2, 3], [-1, 2, 3], [-1, -2, -3], [-1, -2, 3], [1, 2, -3], [-1, 2, -3]]
CASES = {
    "lit-005": {
        "title": "Named feature requirements",
        "sources": ["QuanBench task 03", "QuanBench+ Qiskit task 03 (same formula, not an independent source problem)"],
        "url": "https://github.com/GuoXiaoYu1125/Quanbench/blob/e6cbd58628366c7538cc5a27e9dbf9ebdfc38e1f/QuanBench44.jsonl",
        "license_file": "quanbench.LICENSE", "kernel": "complete", "category": "positive",
        "contract": "review(request) validates all fields before reporting. Each named rule has exactly three alternatives; at least one must match. Locked feature values must also match. Output failed_rules and locked_failures always describe current in input feature/rule order. inspect returns no proposal. complete retains a conforming current; otherwise returns the first conforming Boolean vector in feature order (False before True), or unavailable with null proposal. changes lists changed names in feature order. Repeated/contradictory literals within a rule are allowed. Empty rules are true. No mutation; invalid inputs raise ValueError, text unspecified. CLI reads one JSON request and prints the report.",
        "domain": "Exactly features (distinct nonempty names), rules (unique id, any list of three {feature,enabled:bool}), locked (known-name to bool map), current (bool list matching features), mode inspect|complete. Empty feature lists require no rules or locks. No arbitrary size cap; enumeration is classical and finite.",
        "core": "complete(size,clauses,locked) returns the first Boolean vector in False/True product order satisfying every indexed three-literal clause and fixed-index value; None if absent. conforms evaluates that relation. Valid arguments only: nonnegative size, triples of (index,bool), known indices, and fixed-index mapping. No mutation.",
        "example": {"features": ["x1", "x2", "x3"], "rules": [{"id": f"r{i+1}", "any": [{"feature": f"x{abs(v)}", "enabled": v > 0} for v in row]} for i, row in enumerate(SAT)], "locked": {}, "current": [False]*3, "mode": "complete"},
    },
    "lit-006": {
        "title": "Independent transfer windows",
        "sources": ["QuanBench task 05; values [3,3,1,1,5], weights [2,4,1,3,5], capacity 7"],
        "url": "https://github.com/GuoXiaoYu1125/Quanbench/blob/e6cbd58628366c7538cc5a27e9dbf9ebdfc38e1f/QuanBench44.jsonl",
        "license_file": "quanbench.LICENSE", "kernel": "choose", "category": "positive",
        "contract": "review(request) validates the whole batch first. Eligible items are active entries in catalogue order. Each window is independent; no shared-stock allocation across windows. current report retains listed inactive items and marks infeasible if any are inactive or total weight exceeds capacity. select maximizes total value of indivisible eligible items under capacity; ties use smallest numeric mask in eligible order. proposal includes IDs/weight/value/feasible. transfers follows selected catalogue order with contiguous offsets starting at 0 and item weight as length. inspect has no proposal or transfers. No mutation; invalid input raises ValueError. CLI reads/prints JSON.",
        "domain": "Exactly items and windows lists. Item={id:unique nonempty string, weight:positive int, value:nonnegative int, active:bool}. Window={id:unique nonempty string, capacity:nonnegative int, current:distinct known item IDs, mode:inspect|select}. Bool is not an int. Empty lists allowed; no added numeric cap.",
        "core": "choose(items,capacity) accepts valid ordered item dicts with positive integer weight and nonnegative integer value; nonnegative capacity. Return numeric subset mask maximizing total value under capacity, ties smallest mask. Every item is indivisible and usable at most once. Extra id/active fields are ignored; caller prefilters. Inputs unchanged.",
        "example": {"items": [{"id": f"item{i}", "weight": w, "value": v, "active": True} for i, (w,v) in enumerate(zip([2,4,1,3,5],[3,3,1,1,5]))], "windows": [{"id": "window", "capacity": 7, "current": [], "mode": "select"}]},
    },
    "lit-007": {
        "title": "Signed pair assignment review",
        "sources": ["SupermarQ QAOAVanillaProxy._get_energy_for_bitstring / _gen_sk_hamiltonian / _get_opt_angles"],
        "url": "https://github.com/Infleqtion/client-superstaq/blob/4207004d95490315e519c9d5b07f523367f4b21e/supermarq-benchmarks/supermarq/benchmarks/qaoa_vanilla_proxy.py",
        "license_file": "supermarq.LICENSE", "kernel": "choose", "category": "positive",
        "contract": "review(request) validates one together/apart preference for every unordered pair, rejecting duplicates. current and proposed describe ordered False/True groups, signed score and violated pairs in catalogue-pair order. A satisfied preference contributes +1, an unsatisfied preference -1. inspect reports current only. propose maximizes signed score, ties use smallest numeric membership mask (member i is bit i); report gain and moved members. It need not retain another equally good current. No capacity or group-size constraint, groups may be empty. No mutation; invalid inputs raise ValueError. CLI reads/prints JSON.",
        "domain": "Exactly members (distinct nonempty names), preferences ({left,right,relation:together|apart} for all distinct pairs), current (bool list matching members), mode inspect|propose. Empty/singleton groups allowed. Relation symmetry is explicit; no missing-pair defaults.",
        "core": "score(values,pairs)=sum(w if values[i]!=values[j] else -w). choose(size,pairs) maximizes this over all Boolean vectors; ties smallest numeric mask. Valid complete undirected pairs i<j with w in {-1,+1}; no mutation. Newly authored exact enumeration, not the upstream variational optimizer.",
        "example": {"members": ["a","b","c"], "preferences": [{"left":"a","right":"b","relation":"apart"},{"left":"a","right":"c","relation":"together"},{"left":"b","right":"c","relation":"apart"}], "current": [False]*3,"mode":"propose"},
    },
    "lit-008": {
        "title": "Ordered masking receipts",
        "sources": ["Qiskit HumanEval qiskitHumanEval/53; arithmetic specification and three original examples"],
        "url": "https://github.com/qiskit-community/qiskit-human-eval/blob/c98ba538239fcfd554aa89627ee8026f4b5de450/dataset/dataset_qiskit_test_human_eval.json",
        "license_file": "qhe.LICENSE", "kernel": "encode", "category": "hard_negative",
        "contract": "review(request) validates all records first. For each input row compute the bitwise exclusive-or of left and right, encode exactly eight bits (most significant first), count set bits and update a running sum modulo 256. Return ordered receipts with id/bits/set_bits/counts/prefix_checksum plus record_count and final checksum. counts mode maps the one deterministic bitstring to repetitions; inspect uses null counts but still produces every receipt. Do not replace full output by a sample/aggregate. No mutation; invalid input raises ValueError. CLI reads/prints JSON.",
        "domain": "Exactly records list of {id:unique nonempty string,left:int 0..255,right:int 0..255}, repetitions:positive int, mode inspect|counts. Bool excluded from integers. Empty records allowed. repetitions denotes an exact repeated-outcome count, not random sampling or QPU execution.",
        "core": "encode(a,b) accepts integers 0..255, returns (a XOR b, eight-bit most-significant-first string). Deterministic exact arithmetic, no mutation; valid inputs only.",
        "example": {"records": [{"id":f"r{i}","left":a,"right":b} for i,(a,b) in enumerate([(10,20),(61,9),(47,8)])],"repetitions":1024,"mode":"counts"},
    },
    "lit-009": {
        "title": "Named balance-system review",
        "sources": ["HPL Algorithm: row partial pivoting and Checking the Solution normalized backward error"],
        "url": "https://www.netlib.org/benchmark/hpl/algorithm.html", "license_file": None,
        "kernel": "solve", "category": "hard_negative",
        "contract": "review(request) validates a dense square system then reports current residual. solve mode uses partial-pivoted elimination (largest absolute pivot, first index tie) and back substitution, raises ValueError on exact zero pivot or detected numerical overflow, and returns named float solution, deltas and proposed residual. inspect does not solve and need not reject a singular matrix. Residual vector is Ax-b. scaled_backward_error is its infinity norm divided by machine epsilon*(||A||inf*||x||inf+||b||inf)*n. Zero/zero is 0; nonzero/zero is null. within_requested_limit compares the proposed scaled diagnostic to caller residual_limit; not a quantum-semantic acceptance criterion. Empty system yields empty solution and zero residual. No mutation. This is a small serial Python program, not a compliant HPL performance run.",
        "domain": "Exactly variables (distinct names), matrix (n rows of n finite real numbers), rhs/current (n finite numbers), residual_limit (finite nonnegative number), mode inspect|solve. Bool excluded from numbers. Computation uses Python binary64; values outside that range rejected; detected nonfinite results raise ValueError. No condition-number guarantee or bitwise match to a particular HPL installation.",
        "core": "solve(matrix,rhs): valid square finite float system, copy then pivoted elimination/back substitution, float list; zero pivot/nonfinite result raises ValueError. residual(matrix,rhs,x) computes vector/infinity norm/scaled backward error as described in the context view; valid dimensions only. Inputs unchanged. Newly authored implementation of a documented numerical problem.",
        "example": {"variables":["supply","return"],"matrix":[[0,2],[1,3]],"rhs":[4,7],"current":[0,0],"mode":"solve","residual_limit":1.0},
    },
    "lit-010": {
        "title": "Sparse balance iteration review",
        "sources": ["HPCG CG_ref.cpp unpreconditioned branch and ComputeSPMV_ref.cpp; TestSymmetry.cpp diagnostic idea"],
        "url": "https://github.com/hpcg-benchmark/hpcg/blob/114602d458d1034faa52b71e4c15aba9b3a17698/src/CG_ref.cpp",
        "license_file": "hpcg.LICENSE", "kernel": "advance", "category": "hard_negative",
        "contract": "review(request) validates a symmetric strictly diagonally dominant sparse matrix with positive diagonal. Missing entries are zero, duplicates rejected, entries normalized by variable order. inspect reports only initial Euclidean residual norm. advance follows the supplied unpreconditioned conjugate-direction recurrence from current, up to steps while recurrent residual norm / initial norm exceeds relative_tolerance. Zero initial residual takes zero steps. Return full named iterate, per-step recurrent residual trace, iterations and final directly recomputed residual norm. Budget exhaustion is not exact convergence; do not replace the iterate/trace with an exact solution. Numerical breakdown/nonfinite detected results raise ValueError. No mutation. No multigrid/MPI/rating; not a compliant HPCG run.",
        "domain": "Exactly variables (distinct names), entries ({row,column:known names,value:finite number}), rhs/current (matching finite vectors), steps:nonnegative int, relative_tolerance:finite nonnegative number, mode inspect|advance. Bool excluded from numbers. Symmetry exact after float conversion; diagonal strictly exceeds sum of absolute off-diagonal entries. Empty system allowed. Python binary64 arithmetic, no added size cap.",
        "core": "advance(rows,rhs,current,steps,tolerance) runs the unpreconditioned recurrence on valid symmetric positive strictly diagonally dominant rows of (column,float), returning (iterate,initial_norm,trace). apply is ordered sparse matrix-vector multiplication; dot is ordered dot product. Valid dimensions only, copies current. Stops at budget/relative recurrent residual and checks numerical breakdown. No preconditioner or exact-result substitution.",
        "example": {"variables":["left","right"],"entries":[{"row":"left","column":"left","value":4},{"row":"left","column":"right","value":1},{"row":"right","column":"left","value":1},{"row":"right","column":"right","value":3}],"rhs":[1,2],"current":[0,0],"steps":1,"relative_tolerance":0.0,"mode":"advance"},
    },
}


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def materialize() -> None:
    for case_id, meta in CASES.items():
        folder = HERE / "cases" / case_id
        if (folder / "case.json").exists():
            raise FileExistsError(f"already materialized: {case_id}")
        (folder / "common.py").write_bytes((HERE / "common.py").read_bytes())
        notice = f"Source-task attribution: {'; '.join(meta['sources'])}.\n{meta['url']}\nNew Codex-assisted classical implementation/context, not an upstream classical application or author endorsement.\nNew material/package license NOASSERTION; original rights retained.\n"
        if meta["license_file"]:
            notice += "\nSource license text:\n" + (HERE / "sources" / meta["license_file"]).read_text()
        else:
            notice += "The HPL web specification's page license is not established here. No HPL source code is copied into this application.\n"
        (folder / "NOTICE.txt").write_text(notice)
        public = {"case_id":case_id,"title":meta["title"],"software_contract":meta["contract"],
                  "input_domain":meta["domain"],"execution_assumptions":["Classical inputs and outputs; no workload, quantum hardware, encoding-cost or advantage evidence supplied."]}
        dump(folder / "public_task.json", public)
        dump(folder / "example_request.json", meta["example"])
        output = subprocess.run([sys.executable, "-B", str(folder / "program.py")], input=json.dumps(meta["example"]),
                                text=True, capture_output=True, check=True)
        dump(folder / "example_report.json", json.loads(output.stdout))
        tree = ast.parse((folder / "kernel.py").read_text())
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == meta["kernel"])
        region = {"file":"kernel.py","function":node.name,"start_line":node.lineno,"end_line":node.end_lineno}
        case = json.loads((PARENT / "cases/lit-003/case.json").read_text())
        case.update(case_id=case_id,title=meta["title"],description=meta["contract"],
                    source="Source-task adaptation: " + "; ".join(meta["sources"]) + ". New synthetic classical program; source and changes documented in ADAPTATION.md.",
                    source_url=meta["url"],version="0.1.0",case_type=meta["category"],
                    files=["program.py","kernel.py","common.py"],candidate_regions=[region],classical_tests=["test_program.py"],
                    resource_expectations={"assumptions":public["execution_assumptions"],"limits":{}},
                    semantic_oracle={"kind":"property","description":"DRAFT classical contract tests; no quantum semantic threshold adopted.","config":{"test_artifact":"test_program.py"}},
                    annotation_rationale="DRAFT AI construction proposal, not ground truth. All scientific judgments remain null; category and span are review nominations only. A potentially rejected computation may still be nominated for WHERE.",
                    limitations=["New synthetic classical application from an attributed problem or recurrence; not imported deployed software.","No quantum mapping, practical suitability or harder WHERE result established.","Classical tests support specified behavior on tested inputs, not complete migration correctness.","No new positive quantum families added."])
        case["negative_reason"] = "Provisional scope/retention control for review; not an assertion that no conceivable quantum reformulation exists." if meta["category"]=="hard_negative" else None
        dump(folder / "case.json",case)
        core = dict(public,case_id=f"source-core-{case_id[-3:]}",software_contract=meta["core"],input_domain="Valid kernel arguments as specified; application validation and reports are not part of this core view.")
        dump(folder / "core_task.json",core)


def prepare(output: Path) -> None:
    output.mkdir(parents=True,exist_ok=False)
    task = (ROOT / "pilot/where_review/v0.1/TASK.md").read_text()
    tail = "\nSHARED DRAFT CONTRACTS\n" + (ROOT / "pilot/public_contracts.json").read_text()
    for name in ("case","prediction","migration_plan","phase1_prediction"):
        tail += f"\nSCHEMA {name}\n" + (ROOT / f"schemas/{name}.schema.json").read_text()
    manifest = {"status":"DRAFT_NOT_RUN","model_calls":0,"mother_cases":10,"conditions":[]}
    for case_id in CASES:
        folder=HERE/"cases"/case_id
        messages={}
        for condition in ("A","C"):
            spec = "core_task.json" if condition=="A" else "public_task.json"
            message=task+"\nPUBLIC TASK\n"+(folder/spec).read_text()
            for name in (("kernel.py","NOTICE.txt") if condition=="A" else ("program.py","kernel.py","common.py","NOTICE.txt")):
                text=(folder/name).read_text()
                if name.endswith('.py'):text="\n".join(f"{i}: {line}" for i,line in enumerate(text.splitlines(),1))+"\n"
                message+=f"\nFILE {name}\n"+text
            messages[condition]=message+tail
        hint={k:v for k,v in json.loads((folder/'case.json').read_text())["candidate_regions"][0].items() if k!='function'}
        messages['B']=messages['C']+'\nLOCATION CUE\n'+json.dumps(hint,sort_keys=True)+'\n'
        for condition,message in messages.items():
            filename=f"{case_id}-{condition}.txt";(output/filename).write_text(message)
            manifest['conditions'].append({'case_id':case_id,'condition':condition,'file':filename,'sha256':hashlib.sha256(message.encode()).hexdigest()})
    # Reuse only the four externally sourced parents, not the six local synthetic
    # groups. Their earlier source/spec files remain unchanged.
    old_pairs=json.loads((ROOT/'pilot/reference_cases/v0.3/PAIR_INDEX.json').read_text())['pairs'][:2]
    old_specs={
        'lit-001':ROOT/'pilot/context_adaptations/v0.1/cases/context-001/case.json',
        'lit-002':ROOT/'pilot/reference_cases/v0.1/cases/context-002/case.json',
    }
    c2q_notice=(PARENT/'NOTICE.txt').read_text()
    for number in range(1,5):
        case_id=f'lit-{number:03}'
        messages={}
        for condition in ('A','C'):
            if number<=2:
                view=old_pairs[number-1]['views'][0 if condition=='A' else 1]
                files={name:ROOT/path for name,path in view['source_paths'].items()}
                for name,path in files.items():
                    if hashlib.sha256(path.read_bytes()).hexdigest()!=view['files_sha256'][name]:
                        raise ValueError('changed old public source: '+str(path))
            else:
                view_id=f'source-core-{number:03}' if condition=='A' else case_id
                allowed=('program.py','public_task.json') if condition=='A' else ('program.py','agenda.py' if number==3 else 'reports.py','catalog.py','public_task.json')
                files={name:PARENT/'review_inputs'/view_id/name for name in allowed}
                old_manifest=json.loads((PARENT/'review_inputs/manifest.json').read_text())['files_sha256']
                for name,path in files.items():
                    if hashlib.sha256(path.read_bytes()).hexdigest()!=old_manifest[f'{view_id}/{name}']:
                        raise ValueError('changed old public source: '+str(path))
            message=task+'\nPUBLIC TASK\n'+files['public_task.json'].read_text()
            for name,path in files.items():
                if name=='public_task.json':continue
                text='\n'.join(f'{i}: {line}' for i,line in enumerate(path.read_text().splitlines(),1))+'\n'
                message+=f'\nFILE {name}\n'+text
            messages[condition]=message+'\nFILE NOTICE.txt\n'+c2q_notice+tail
        spec_path=old_specs[case_id] if number<=2 else PARENT/'cases'/case_id/'case.json'
        hint={k:v for k,v in json.loads(spec_path.read_text())['candidate_regions'][0].items() if k!='function'}
        messages['B']=messages['C']+'\nLOCATION CUE\n'+json.dumps(hint,sort_keys=True)+'\n'
        for condition,message in messages.items():
            filename=f'{case_id}-{condition}.txt';(output/filename).write_text(message)
            manifest['conditions'].append({'case_id':case_id,'condition':condition,'file':filename,'sha256':hashlib.sha256(message.encode()).hexdigest()})
    manifest['conditions'].sort(key=lambda r:(r['case_id'],r['condition']))
    for row in manifest['conditions']:
        message=(output/row['file']).read_text()
        public=json.JSONDecoder().raw_decode(message.split('\nPUBLIC TASK\n',1)[1])[0]
        row['prediction_case_id']=public['case_id']
    manifest['note']='Ten sourced groups, related mathematical structures; A/B/C are not independent cases. New input version; no mixing with historical scores.'
    manifest['task_sha256']=hashlib.sha256(task.encode()).hexdigest()
    dump(output/'manifest.json',manifest)


if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__);g=p.add_mutually_exclusive_group(required=True)
    g.add_argument('--materialize',action='store_true');g.add_argument('--prepare',type=Path)
    a=p.parse_args()
    if a.materialize:materialize()
    else:prepare(a.prepare)
