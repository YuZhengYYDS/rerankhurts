# RerankHuts: code and experimental artifacts

**What Survives in Budgeted RAG Pipelines? Source Retention and Fact Coverage**

For the ICDE artifact entry point, start with [ARTIFACTS.md](ARTIFACTS.md). The [guide.md](guide.md) provides a Chinese directory map and common commands.

This repository contains code, datasets, experimental outputs, and supporting records for the study. The manuscript and its historical snapshots are not included in the current repository.

Authors: Zheng Yu, Jie Li, Boyang Wang, Xinle Yang and Jingbang Chen. Zheng Yu and Jie Li share **Equal Contribution**; Jingbang Chen is the corresponding author.

## Repository layout

| Directory | Purpose |
| --- | --- |
| [data/](data/README.md) | Oncology corpora, question sets, source configuration and data reports. |
| [metadata/](metadata/README.md) | Repository file manifest, release status and data-layout provenance. |
| [rerankhuts/](rerankhuts/) | Unified command dispatcher: `python -m rerankhuts`. |
| [experiments/](experiments/README.md) | Experimental implementations, frozen inputs, runs and independent evaluations. |
| [scripts/](scripts/) | Build, verification, release packaging and analysis commands. Historical table helpers are grouped under `scripts/paper/`. |
| [validation/](validation/README.md) | Independent evaluators and historical verification records. |
| [legacy/](legacy/README.md) | Historical data preparation, evaluation and result utilities, including all five former root Python scripts. |
| [archive/](archive/) | Historical source-code snapshots and related records. |
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

The lockfile covers Windows and Linux. Use the `gpu` environment for model inference. Model execution and historical API-based workflows require explicit commands. Some historical manuscript, packaging, and verification commands expect files that are no longer included and need updating before use.

```bash
# Inspect an execution plan without running it.
pixi run --locked workflow --dry-run e3

```

The five relocated tools have explicit dispatcher/Pixi commands: `legacy-normalize`, `legacy-eval`, `legacy-score`, `legacy-analysis` and `legacy-summarize`. They retain their historical environment-variable configuration. See [legacy/README.md](legacy/README.md) before executing a historical pipeline.

## Experimental evidence and reanalysis

The original E3 workload contains 155 questions across 20 configurations (3,100 records). The controlled `pilot_v2` workload contains 120 tasks across 20 configurations (2,400 records). The separate `strengthening_v1` workload contains 360 worlds, 720 tasks and 124 configurations (89,280 main inference records), with separately recorded answer and request-timing studies. Answer-study records are available under [the strengthening results](experiments/strengthening/results/strengthening_v1/answers/).

```bash
pixi run --locked e0
pixi run --locked analyze-e3
pixi run --locked interactions-e3
pixi run --locked strengthen-verify --require-complete
```

Reanalysis outputs go under `build/`. Historical experiment data, traces and statistical results retain their recorded identities; manuscript figure files are not included.

The authors report that two reviewers completed the 60-world human semantic audit; the review records have not yet been added to this repository. The updated 377-fact oncology annotations and matching results are available in [the coverage package](experiments/supplements/oncology_coverage_v1/); the older frozen E3 results remain a separate historical version. The annotation snapshot identifies Codex assistant as its author and records no domain adjudication; the authors report that expert review was completed later, but the supporting records are not yet included. The repository is public, but the original human-review records, oncology expert-review records, and a complete from-scratch reproducibility audit are still needed before claiming the EAB artifact is complete. See [metadata/release_status.json](metadata/release_status.json) and [docs/EXPERIMENT_SCOPE.md](docs/EXPERIMENT_SCOPE.md) for provenance and scope.

## Releases and provenance

The [GitHub releases](https://github.com/YuZhengYYDS/rerankhurts/releases) retain separate code and results archives. Manuscript-containing archives have been removed. Frozen experiment manifests, release checksums and historical documentation may still reference removed files; use [metadata/MANIFEST.json](metadata/MANIFEST.json) for the current source-tree inventory.

The active repository is [YuZhengYYDS/rerankhurts](https://github.com/YuZhengYYDS/rerankhurts). See [validation/](validation/) for historical verification records.

Code licensing is in [LICENSE](LICENSE); third-party corpus material retains its own source terms.
