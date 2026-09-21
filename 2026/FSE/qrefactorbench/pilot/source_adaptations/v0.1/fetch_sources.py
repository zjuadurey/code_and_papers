"""Reproduce two pinned source excerpts; never execute downloaded code."""

import ast
import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen

REVISION = "c5b457cf425c31e91bae829503ece6e92646dd0a"
BASE = f"https://huggingface.co/datasets/boshuai1/c2q-dataset/resolve/{REVISION}/"
SELECTION = {"lit-001": (164, "maxcut_bruteforce"),
             "lit-002": (427, "min_vertex_cover_bruteforce")}


def main() -> None:
    root = Path(__file__).resolve().parent
    output = root / "sources"
    output.mkdir(exist_ok=True)
    csv_bytes = urlopen(BASE + "python_programs.csv", timeout=30).read()
    rows = list(csv.DictReader(io.StringIO(csv_bytes.decode("utf-8"))))
    card = urlopen(BASE + "README.md", timeout=30).read()
    artifacts = {"DATASET_CARD.md": card}
    metadata = {"dataset": "boshuai1/c2q-dataset", "revision": REVISION,
                "csv_url": BASE + "python_programs.csv",
                "csv_sha256": hashlib.sha256(csv_bytes).hexdigest(),
                "row_count": len(rows), "row_numbering": "1-based data rows, excluding header",
                "source_license": "CC-BY-4.0", "selection": {}}
    for case_id, (number, function) in SELECTION.items():
        row = rows[number - 1]
        # These selected CSV fields contain literal backslash-n separators.
        # No unicode_escape decoding, stripping or other source repair is used.
        source = row["code_snippet"].replace("\\n", "\n")
        tree = ast.parse(source)
        node = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function)
        kernel = "\n".join(source.splitlines()[node.lineno - 1:node.end_lineno]) + "\n"
        if case_id == "lit-002":
            kernel = "import itertools\n\n" + kernel
        artifacts[f"{case_id}.row.json"] = (json.dumps(row, indent=2) + "\n").encode()
        artifacts[f"{case_id}.decoded.py"] = source.encode()
        artifacts[f"{case_id}.kernel.py"] = kernel.encode()
        metadata["selection"][case_id] = {
            "data_row": number, "original_function": function,
            "original_label": row["labels"],
            "original_field_sha256": hashlib.sha256(row["code_snippet"].encode()).hexdigest(),
            "decoded_sha256": hashlib.sha256(source.encode()).hexdigest(),
            "kernel_sha256": hashlib.sha256(kernel.encode()).hexdigest(),
            "normalization": "literal \\n to newline only; function body unchanged; demo removed",
        }
    metadata["files_sha256"] = {k: hashlib.sha256(v).hexdigest() for k, v in artifacts.items()}
    artifacts["manifest.json"] = (json.dumps(metadata, indent=2) + "\n").encode()
    for name, content in artifacts.items():
        target = output / name
        if target.exists() and target.read_bytes() != content:
            raise SystemExit(f"Refusing to overwrite different source evidence: {target}")
    for name, content in artifacts.items():
        (output / name).write_bytes(content)
    print("Two pinned excerpts saved/verified; no source code executed.")


if __name__ == "__main__":
    main()
