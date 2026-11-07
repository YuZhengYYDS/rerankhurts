# Repository guide

Run commands from the repository root. The [v25 artifact guide](docs/V25_ARTIFACT_GUIDE.md)
maps the current manuscript to its input files, configurations, results and traces.

## Starting points

| Task | Location |
| --- | --- |
| Read the current manuscript | [paper/main.pdf](paper/main.pdf) |
| Edit or compile the manuscript | [paper/README.md](paper/README.md), entry file `main.tex` |
| Find original Oncology inputs and sources | [data/README.md](data/README.md) |
| Inspect recorded completion status | [metadata/release_status.json](metadata/release_status.json) |
| Understand the implementation | [docs/CODE_GUIDE.md](docs/CODE_GUIDE.md) |
| Locate reported measurements | [docs/RESULTS_GUIDE.md](docs/RESULTS_GUIDE.md) |
| Inspect the 60-world review records | [audit/reviews/README.md](experiments/strengthening/data/strengthening_v1/audit/reviews/README.md) |

## Layout

```text
paper/                       Manuscript, bibliography, IEEE template and figures
data/oncology/corpus/         Original and expanded corpora
data/oncology/questions/      Original and expanded question files
data/oncology/sources/        Source configuration and URL lists
data/oncology/reports/        Corpus construction and question screening reports
metadata/                    Inventory, current status and migration records
rerankhuts/                  Unified CLI and historical path resolution
experiments/                 Frozen inputs, implementations, traces and results
experiments/supplements/     Versioned v25 supplementary analyses and inputs
validation/                  Independent checks and dated verification records
scripts/                     Analysis, build, review verification and packaging
legacy/                      Historical data preparation and research utilities
archive/                     Preserved historical source and document snapshots
docs/                        Maintained documentation
tests/                       Tests
build/                       Local compilation, reanalysis and new-run outputs
```

The root keeps `README.md`, this guide, `LICENSE`, Pixi definitions and Git/environment
configuration. Experimental JSON/JSONL/CSV files and Python tools live in the
corresponding subdirectories.

## Frozen data

| Location | Contents |
| --- | --- |
| `data/oncology/corpus/` | `corpus_chunks_v1.jsonl` (6,785 chunks); `corpus_chunks_v2.jsonl` (7,124 chunks) |
| `data/oncology/questions/` | `questions.jsonl` (100 questions); expanded prepurge (187), validated (155), and judge-sample (40) files |
| `data/oncology/sources/` | `data_sources.json`, `urls.txt` |
| `data/oncology/reports/` | Corpus expansion and question leak-screening CSVs |
| `experiments/simulation/data/pilot_v2/` | Separate controlled pilot inputs |
| `experiments/strengthening/data/strengthening_v1/` | Main 360-world benchmark inputs and audit packet |
| `experiments/supplements/oncology_coverage_v1/` | Final annotated-support workload and its exact trace index |

Original Oncology files retain their bytes and hashes. Historical manifests may
use former root filenames; [rerankhuts/paths.py](rerankhuts/paths.py) resolves the
known relocations while preserving identity checks. The final annotated workload
uses a separately versioned question file rather than replacing original inputs.

## Environment and commands

```bash
pixi install --locked
pixi run --locked workflow --help
pixi run --locked status
```

The lockfile covers Windows and Linux. Use `gpu` for model/tokenizer dependencies
and `paper` for compilation. Weights are not included in the release.

| Command | Action |
| --- | --- |
| `pixi run --locked verify` | Check historical E0/E3 and pilot frozen identities |
| `pixi run --locked strengthen-verify --require-complete` | Check the complete main benchmark and its downstream records |
| `pixi run --locked test` | Run tests in the selected environment |
| `pixi run --locked e0` | Recompute the historical audit under `build/reanalysis/e0/` |
| `pixi run --locked analyze-e3` | Recompute 16 E3 contrasts under `build/reanalysis/e3/` |
| `pixi run --locked interactions-e3` | Recompute the separate eight E3 interactions |
| `pixi run --locked stage-reanalysis` | Recompute matched stage transitions |
| `pixi run --locked packing-reanalysis` | Recompute packing recovery and loss counts |
| `pixi run --locked oncology-coverage` | Rescore annotated support on saved character intervals |
| `python scripts/plot_v25_complementary.py` | Recreate current Fig. 11 from the final Oncology and pilot results |
| `python scripts/check_world_review_records.py` | Check the two supplied detailed review records against frozen source files |
| `pixi run --locked paper-tables` | Regenerate historical tables under `build/reanalysis/tables/` |
| `pixi run --locked -e paper paper` | Compile the current manuscript; scratch stays under `build/paper/` |
| `python scripts/check_manuscript.py` | Check compiled structure, references, figures, tables and page budget |
| `pixi run --locked package --split --verify` | Build and verify full, paper, code and result archives |

Use `pixi run --locked workflow --dry-run e3` to inspect an invocation. New E3
inference uses the relocated inputs and writes to `build/runs/e3/`; the delivered
run remains in `experiments/runs/e3_m3/`. Input path strings belong to run identity,
so a new path cannot be used to resume a frozen run with a different identity.

The five `legacy-*` commands retain their original environment-variable interfaces.
See [legacy/README.md](legacy/README.md) before running a historical pipeline.

## Inventories and output protection

- [metadata/MANIFEST.json](metadata/MANIFEST.json) inventories current packageable
  files by size and SHA-256, excluding its own digest.
- [metadata/release_status.json](metadata/release_status.json) indexes current
  manuscript, author and experiment status alongside dated historical records.
- [metadata/data_layout.json](metadata/data_layout.json) records the original
  data migration and preserved identities.
- [archive/README.md](archive/README.md) indexes historical manuscript/source assets.

Each generated ZIP also has an independent root `MANIFEST.json` for its members.
New outputs use `build/` or an explicitly separate directory. The supplied paper
figures remain in `paper/figures/`; historical redraws and the current Fig. 11
redraw have separate output paths. Current editable sources for Figs. 1-3 remain
in [paper/figures/drawio/](paper/figures/drawio/).

Maintained guides are English. Frozen inputs, source quotations, historical
reports and archived documentation retain their original language and bytes;
English explanatory companions do not replace those source records.
