# RerankHuts: manuscript, code and experimental artifacts

**What Survives the Context Budget? Source Retention and Fact Coverage in RAG**

Start with [guide.md](guide.md) for the directory map, data locations and common commands.

The current manuscript is in [paper/](paper/README.md), with [main.tex](paper/main.tex) and the [compiled PDF](paper/main.pdf). The source project imported on 2026-10-26 contains the revised `-v2.pdf` figures for Figures 4–12. Figures 1–3 were updated on 2026-10-27 from the supplied draw.io sources, available in [paper/figures/drawio/](paper/figures/drawio/). The paper directory is a self-contained Overleaf project; compiler scratch and validation reports live outside it.

Authors: Zheng Yu, Jie Li, Boyang Wang and Jingbang Chen. Zheng Yu and Jie Li share **Equal Contribution**; Jie Li and Boyang Wang are affiliated with The Chinese University of Hong Kong, Shenzhen. Jingbang Chen is the corresponding author. The authoritative author block is [authors.tex](paper/authors.tex).

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

Reanalysis outputs go under `build/`. Frozen experiment data, traces and statistical results retain their recorded identities. The current `-v2.pdf` figures are supplied manuscript assets; historical redraw tools preserve the earlier figure provenance and do not regenerate or overwrite those revised PDFs. Current editable sources for Figures 1–3 are in [paper/figures/drawio/](paper/figures/drawio/). The archived draw.io sources and original SVG icon catalog remain available under [archive/paper_20261022/figures/drawio/](archive/paper_20261022/figures/drawio/).

Human semantic annotation and independent external-workload replication retain the statuses recorded in the experiment documentation; synthetic or model-generated assessments are not human annotations. See [docs/EXPERIMENT_SCOPE.md](docs/EXPERIMENT_SCOPE.md) for the limits of the evidence.

## Releases and provenance

`package --split --verify` writes `rerankhuts_icde2027.zip`, `paper_icde2027_clean.zip`, the separate code/results archives, manifests and checksums to `dist/`. Archives use deterministic member ordering and exclude environments, model caches, credentials and compiler scratch. Package verification binds manuscript inputs to the current build record as well as checking archive paths, sizes and hashes.

The active repository is [YuZhengYYDS/rerankhurts](https://github.com/YuZhengYYDS/rerankhurts). Earlier released packages and historical verification reports retain their original dates and scope. Current manuscript checks and the 2026-10-26 import/organization record are in [validation/manuscript_checks.json](validation/manuscript_checks.json) and [validation/repository_update_20261026.json](validation/repository_update_20261026.json).

Code licensing is in [LICENSE](LICENSE); third-party corpus material retains its own source terms.
