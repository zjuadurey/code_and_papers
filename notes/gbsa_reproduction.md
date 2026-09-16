# GBSA reproduction: source audit and blocker

Status: **NOT REPRODUCED — SOURCE_BLOCKED**. No GBSA implementation or
performance measurement is claimed. This is not a negative result for GBSA.

## Paper and artifact

- Chuan-Chi Wang, Chia-Heng Tu, Shih-Hao Hung, *Toward Efficient Quantum Circuit
  Simulation with Memory and I/O Reduction through Gate Block Search Algorithm*.
- RACS 2025, article 11, pp. 11:1–11:8; institution records online publication
  on 2026-02-04. [Publisher DOI](https://doi.org/10.1145/3769002.3769982).
- [Author institution record](https://researchoutput.ncku.edu.tw/zh/publications/toward-efficient-quantum-circuit-simulation-with-memory-and-io-re/)
  supplies the title, authors, abstract and bibliographic metadata, but no full
  paper or executable artifact. It describes maximizing gates per block to reuse
  state data and reduce memory/storage access, evaluated on an AMD 64-core CPU.
- Official repository/artifact: **not found in the searches performed**, not a
  claim that none exists. Implementation language, exact simulator/backend,
  software license, storage policy and recommended parameters: **unverified**.
- No authors were contacted, no accounts created and no paid access purchased.

## Retrieval attempts (2026-09-16 UTC)

1. ACM DOI landing page, `/doi/abs/`, `/doi/full/`, `/doi/pdf/` and `/doi/epdf/`:
   unavailable to the web reader; direct PDF/EPDF requests returned HTTP 403.
   An ordinary headless-browser navigation timed out without a usable document.
2. Crossref DOI metadata: available; links only to the inaccessible ACM PDF,
   no license or alternate full-text URL returned.
3. OpenAlex DOI record: `oa_status=closed`, `any_repository_has_fulltext=false`;
   Semantic Scholar DOI record: empty `openAccessPdf.url`.
4. GitHub repository/code searches for the exact paper title, DOI, GBSA with
   quantum context, and `findMaxGate`; author-affiliated nckuasrlab public repo
   list; no verified official GBSA implementation located.
5. Zenodo exact “Gate Block Search” query returned zero records. An exact-title
   arXiv search returned no results. Author home page did not supply this paper;
   its linked PAS laboratory host could not be resolved.
6. An independently indexed paper-reader log contains the title only, not text
   or code. It is not treated as algorithm evidence.

Retrieved metadata hashes and request outcomes are recorded in
`results/gbsa_comparison/source_audit.json`. Downloaded external material stays
under ignored `external/gbsa-paper/`; an HTML error saved with a `.pdf` suffix is
explicitly **not** counted as a retrieved paper.

## Related primary documents inspected only to find the missing algorithm

The same authors' [Queen preprint](https://arxiv.org/abs/2406.14084), Section IV,
Algorithm 1, describes dependency updates, selecting a maximum gate block,
qubit rearrangement and block execution. The `findMaxGate` function is abstract
at that level. Their [later preprint](https://arxiv.org/abs/2604.12256), Section
4.2, calls GBSA as a subroutine but does not provide the missing RACS algorithm.
These documents cannot establish that an independently guessed selector is the
GBSA policy in the requested paper. No Queen, Atlas, Hsu or GPU performance
baseline was substituted, and no new research direction was pursued.

## What was implemented / omitted / parameters

Implemented: provenance audit, explicit unavailable-result schemas, canonical
workload/hash fairness manifest, and combined tables preserving measured QDAO
and QThin values with GBSA cells marked NA.

Not implemented: a guessed gate-block selector, a replacement simulator, or any
GBSA kernel. All GBSA correctness/performance cases are NOT_RUN, not zero-error
validated cases. Parameters remain NA. Inventing a generic greedy grouping and
labelling it “GBSA reproduction” would invalidate the requested comparison.

## Resume condition

Obtain a readable copy of DOI 10.1145/3769002.3769982 or a verifiable author
artifact. Then map the published search, dependencies, block limits and storage
execution to implementation; document deviations; validate n≤12; run the exact
frozen 20/22/24q inputs with three repetitions. Keep Phase A frozen. Only after
that can the GBSA column and QThin-versus-GBSA claims be populated.
