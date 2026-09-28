---
license: cc-by-4.0
task_categories:
- text-classification
- text-generation
- other
tags:
- quantum-computing
- quantum-software-engineering
- benchmark
- c2q
pretty_name: C2|Q> Dataset
---

# C2|Q> Dataset

This repository contains the released dataset materials associated with the paper:

**C2|Q>: A Robust Framework for Bridging Classical and Quantum Software Development**  
arXiv: [2510.02854](https://arxiv.org/abs/2510.02854)  
TOSEM 2026  
DOI: [10.1145/3803018](https://doi.org/10.1145/3803018)

## Contents

This dataset repository provides cleaned public inputs used for artifact inspection and reproduction, including:

- synthetic Python program inputs
- backup CSV data
- generated JSON DSL examples
- JSON DSL smoke subset
- optional usability-comparison materials

## Main Files

- `python_programs.csv`
- `data.csv`
- `json_dsl/`
- `json_dsl_smoke/`

## Source Project

- GitHub: [C2-Q/C2Q](https://github.com/C2-Q/C2Q)
- Paper (arXiv): [2510.02854](https://arxiv.org/abs/2510.02854)
- Paper (TOSEM): [10.1145/3803018](https://doi.org/10.1145/3803018)

## Archival Record

The archival evaluation record is preserved on Zenodo:

- Zenodo DOI: [10.5281/zenodo.17071667](https://doi.org/10.5281/zenodo.17071667)

Hugging Face is provided for discoverability and easier browsing. Zenodo remains the archival source.

## Intended Use

- artifact inspection
- lightweight benchmarking
- JSON-based reproduction support
- supporting materials for the C2|Q> artifact

## Limitations

- this is a cleaned public mirror, not the complete repository
- generated local artifact outputs are not included here
- source-code execution and `make`-based workflows remain in the GitHub repository

## License

CC-BY-4.0
