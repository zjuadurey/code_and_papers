"""Fetch pinned review excerpts; parse, but never execute, downloaded code."""

import argparse
import ast
import csv
import hashlib
import io
import json
from pathlib import Path
from urllib.request import urlopen

REVISION = "c5b457cf425c31e91bae829503ece6e92646dd0a"
BASE = f"https://huggingface.co/datasets/boshuai1/c2q-dataset/resolve/{REVISION}/"
ROWS = {87: "clique_brute_force", 88: "clique_greedy", 93: "clique_bitmask",
        94: "clique_backtracking", 97: "greedy_kcolor_adj_matrix", 98: "kcolor_backtracking",
        101: "kcolor_backtrack_partial", 103: "kcolor_with_color_sets",
        388: "min_vertex_cover_bruteforce", 431: "min_vertex_cover_bnb"}


def fetch(output: Path) -> None:
    data = urlopen(BASE + "python_programs.csv", timeout=30).read()
    card = urlopen(BASE + "README.md", timeout=30).read()
    rows = list(csv.DictReader(io.StringIO(data.decode())))
    artifacts = {"DATASET_CARD.md": card}
    manifest = {"dataset": "boshuai1/c2q-dataset", "revision": REVISION,
                "csv_url": BASE + "python_programs.csv", "csv_sha256": hashlib.sha256(data).hexdigest(),
                "row_count": len(rows), "row_numbering": "1-based data rows, excluding header",
                "source_license": "CC-BY-4.0 (dataset card); new application code NOASSERTION",
                "selection": {}, "normalization": "literal backslash-n to newline; remove top-level demos only"}
    for number, name in ROWS.items():
        row = rows[number - 1]
        source = row["code_snippet"].replace("\\n", "\n")
        tree = ast.parse(source)
        functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)]
        assert any(n.name == name for n in functions)
        # Keep all function definitions for row 431's is_cover dependency.
        kernel = "\n\n".join(ast.get_source_segment(source, n) for n in functions) + "\n"
        if number == 431:
            kernel = "import itertools\n\n" + kernel
        artifacts[f"row-{number}.json"] = (json.dumps(row, indent=2) + "\n").encode()
        artifacts[f"row-{number}.decoded.py"] = source.encode()
        artifacts[f"row-{number}.kernel.py"] = kernel.encode()
        manifest["selection"][str(number)] = {"function": name, "original_label": row["labels"],
             "original_field_sha256": hashlib.sha256(row["code_snippet"].encode()).hexdigest()}
    manifest["files_sha256"] = {name: hashlib.sha256(content).hexdigest() for name, content in artifacts.items()}
    artifacts["manifest.json"] = (json.dumps(manifest, indent=2) + "\n").encode()
    output.mkdir(parents=True, exist_ok=False)
    for name, content in artifacts.items():
        (output / name).write_bytes(content)
    print("Ten pinned source records saved; no downloaded code executed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path)
    fetch(parser.parse_args().output)
