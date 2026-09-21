"""Fetch pinned reference artifacts without importing or executing them."""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

PINS = {
    "quanbench": ("GuoXiaoYu1125/Quanbench", "e6cbd58628366c7538cc5a27e9dbf9ebdfc38e1f"),
    "quanplus": ("JawadKotaichh/quanbench-plus", "2dfd1a863b13d3762a734ed96742adb39e65e34b"),
    "qhe": ("qiskit-community/qiskit-human-eval", "c98ba538239fcfd554aa89627ee8026f4b5de450"),
    "supermarq": ("Infleqtion/client-superstaq", "4207004d95490315e519c9d5b07f523367f4b21e"),
    "mqt": ("munich-quantum-toolkit/bench", "c05b1966274d8a8488bf777d3cc78a39ea9d7857"),
    "pqid": ("Elias-Abebe-Gasparini/PQID-Bench", "f4bafb4ce96569dbffe82c2e44f142a81e4ee27e"),
    "hpcg": ("hpcg-benchmark/hpcg", "114602d458d1034faa52b71e4c15aba9b3a17698"),
}
FILES = [
    ("quanbench", "QuanBench44.jsonl", "quanbench.jsonl"),
    ("quanbench", "Quanbench_eval/evaluation.py", "quanbench_evaluation.py"),
    ("quanbench", "LICENSE", "quanbench.LICENSE"),
    ("quanplus", "prompts/qiskit.jsonl", "quanplus_qiskit.jsonl"),
    ("quanplus", "utils/get_kl_div.py", "quanplus_kl.py"),
    ("quanplus", "LICENSE", "quanplus.LICENSE"),
    ("qhe", "dataset/dataset_qiskit_test_human_eval.json", "qhe.json"),
    ("qhe", "LICENSE", "qhe.LICENSE"),
    ("supermarq", "supermarq-benchmarks/supermarq/benchmarks/qaoa_vanilla_proxy.py", "supermarq.py"),
    ("supermarq", "LICENSE", "supermarq.LICENSE"),
    ("mqt", "src/mqt/bench/benchmarks/qaoa.py", "mqt_qaoa.py"),
    ("mqt", "LICENSE", "mqt.LICENSE"),
    ("pqid", "scripts/run_pqid_bench_executable_validity_check.py", "pqid_worker.py"),
    ("pqid", "LICENSE.md", "pqid.LICENSE.md"),
    ("pqid", "LICENSES/MIT.txt", "pqid.MIT.txt"),
    ("pqid", "LICENSES/CC-BY-4.0.txt", "pqid.CC-BY-4.0.txt"),
    ("hpcg", "src/CG_ref.cpp", "hpcg_CG.cpp"),
    ("hpcg", "src/ComputeSPMV_ref.cpp", "hpcg_SPMV.cpp"),
    ("hpcg", "src/TestSymmetry.cpp", "hpcg_symmetry.cpp"),
    ("hpcg", "LICENSE", "hpcg.LICENSE"),
]


def fetch(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=False)
    records = []
    for project, path, name in FILES:
        repo, sha = PINS[project]
        url = f"https://raw.githubusercontent.com/{repo}/{sha}/{path}"
        data = urlopen(url, timeout=40).read()
        (output / name).write_bytes(data)
        records.append({"project": project, "revision": sha, "url": url, "file": name,
                        "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    for name, url in [("hpl_algorithm.html", "https://www.netlib.org/benchmark/hpl/algorithm.html"),
                      ("quanplus_paper.html", "https://arxiv.org/html/2604.08570v2")]:
        data = urlopen(url, timeout=40).read()
        (output / name).write_bytes(data)
        records.append({"url": url, "file": name, "revision": None, "bytes": len(data),
                        "sha256": hashlib.sha256(data).hexdigest(), "note": "Fetched page snapshot; URL not an immutable git object."})
    (output / "manifest.json").write_text(json.dumps(records, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    fetch(parser.parse_args().output)
