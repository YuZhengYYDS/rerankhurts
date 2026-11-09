# RerankHuts: manuscript, code and experimental artifacts

**What Survives in Budgeted RAG Pipelines? Source Retention and Fact Coverage**

Start with [guide.md](guide.md) for the directory map, data locations and common commands.

The current manuscript is in [paper/](paper/README.md), with [main.tex](paper/main.tex) and the [compiled PDF](paper/main.pdf). It is based on the author-supplied `Zheng_Yu_s_Great_Work.zip`, with the subsequent title, abstract, introduction, author and emphasis edits. Figures 4 and 11 use the supplied v3 PDFs; the editable sources for Figures 1–3 are in [paper/figures/drawio/](paper/figures/drawio/). The paper directory is a self-contained Overleaf project; compiler scratch and validation reports live outside it.

Authors: Zheng Yu, Jie Li, Boyang Wang, Xinle Yang and Jingbang Chen. Zheng Yu and Jie Li share **Equal Contribution**; Jie Li, Boyang Wang and Xinle Yang are affiliated with The Chinese University of Hong Kong, Shenzhen. Jingbang Chen is the corresponding author. The authoritative author block is [authors.tex](paper/authors.tex).

## Repository layout

| Directory | Purpose |
| --- | --- |
| [paper/](paper/README.md) | Current manuscript, bibliography, IEEE template and supplied figure PDFs. |
| [data/](data/README.md) | Oncology corpora, question sets, source configuration and data reports. |
| [metadata/](metadata/README.md) | Repository file manifest, release status and data-layout provenance. |
| [rerankhuts/](rerankhuts/) | Unified command dispatcher: `python -m rerankhuts`. |
| [experiments/](experiments/README.md) | Experimental implementations, frozen inputs, runs and independent evaluations. |
| [scripts/](scripts/) | Build, verification, release packaging and analysis commands. Historical table helpers are grouped under `scripts/paper/`. |
| [validation/](validation/README.md) | Independent evaluators and verification records. Current paper checks are in `validation/manuscript_checks.json`. |
| [legacy/](legacy/README.md) | Historical data preparation, evaluation and result utilities, including all five former root Python scripts. |
| [archive/](archive/README.md) | Byte-preserved historical paper and source snapshots used by provenance checks. |
| [tests/](tests/) | Protocol, oracle, CLI, integrity and packaging tests. |
| [docs/](docs/) | [Code guide](docs/CODE_GUIDE.md), [result guide](docs/RESULTS_GUIDE.md), [experiment scope](docs/EXPERIMENT_SCOPE.md) and [strengthening guide](docs/STRENGTHENING_GUIDE.md). |
| `build/`, `dist/` | Local compiler/reanalysis scratch and generated release packages; excluded from Git. |

The repository root has no Python script shims. The maintained versions of `generate_normalized_questions.py`, `run_rag_eval.py`, `score_retrieval.py`, `paper_support_analysis.py` and `summarize_supplement_results.py` are in `legacy/`. Their original source bytes remain in `archive/code_20261022/`, so historical input manifests can still verify the exact implementations they recorded.

## Environment and entry points

Install [Pixi](https://pixi.prefix.dev/) and run from the repository root:

```bash
pixi install --locked
pixi run --locked workflow --help
pixi run --locked status
pixi run --locked verify
pixi run --locked test
```

The lockfile covers Windows and Linux. Use the `gpu` environment for model inference and the `paper` environment for compilation. Model execution and historical API-based workflows are explicit commands; repository organization and manuscript import do not rerun them.

```bash
# Inspect an execution plan without running it.
pixi run --locked workflow --dry-run e3

# Compile the current manuscript; scratch stays under build/paper/.
pixi run --locked -e paper paper
python scripts/check_manuscript.py

# Recompute historical table outputs under build/, without editing paper/.
pixi run --locked paper-tables

# Create and verify full, manuscript, code and result packages.
pixi run --locked package --split --verify
pixi run --locked verify-package
```

The five relocated tools have explicit dispatcher/Pixi commands: `legacy-normalize`, `legacy-eval`, `legacy-score`, `legacy-analysis` and `legacy-summarize`. They retain their historical environment-variable configuration. See [legacy/README.md](legacy/README.md) before executing a historical pipeline.

## Experimental evidence and reanalysis

The original E3 workload contains 155 questions across 20 configurations (3,100 records). The controlled `pilot_v2` workload contains 120 tasks across 20 configurations (2,400 records). The separate `strengthening_v1` workload contains 360 worlds, 720 tasks and 124 configurations (89,280 main inference records), with separately recorded answer and request-timing studies. The matched 2048-token answer follow-up is documented with the historical Figure 9 source records in [the archived paper](archive/paper_20261022/figures/source_data/fig09_answers/).

```bash
pixi run --locked e0
pixi run --locked analyze-e3
pixi run --locked interactions-e3
pixi run --locked strengthen-verify --require-complete
```

Reanalysis outputs go under `build/`. Frozen experiment data, traces and statistical results retain their recorded identities. The v2/v3 figure PDFs are supplied manuscript assets; historical redraw tools do not regenerate or overwrite them. Editable sources for Figures 1–3 are in [paper/figures/drawio/](paper/figures/drawio/). Earlier sources and the original SVG icon catalog remain in [archive/paper_20261022/figures/drawio/](archive/paper_20261022/figures/drawio/).

The authors report that two reviewers completed the 60-world human semantic audit; the review records have not yet been added to this repository. The updated 377-fact oncology annotations and results underlying the current manuscript are also pending upload. The existing frozen audit and oncology results document earlier states and must not be presented as the updated records. Before the EAB submission, add the missing materials and make the complete artifact openly accessible. See [metadata/release_status.json](metadata/release_status.json) and [docs/EXPERIMENT_SCOPE.md](docs/EXPERIMENT_SCOPE.md) for provenance and scope.

## Releases and provenance

`package --split --verify` writes `rerankhuts_icde2027.zip`, `paper_icde2027_clean.zip`, the separate code/results archives, manifests and checksums to `dist/`. Archives use deterministic member ordering and exclude environments, model caches, credentials and compiler scratch. Package verification binds manuscript inputs to the current build record as well as checking archive paths, sizes and hashes.

The active repository is [YuZhengYYDS/rerankhurts](https://github.com/YuZhengYYDS/rerankhurts). Earlier released packages and historical verification reports retain their original dates and scope. Current manuscript checks and the 2026-10-26 import/organization record are in [validation/manuscript_checks.json](validation/manuscript_checks.json) and [validation/repository_update_20261026.json](validation/repository_update_20261026.json).

Code licensing is in [LICENSE](LICENSE); third-party corpus material retains its own source terms.
