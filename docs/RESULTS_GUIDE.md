# Results and manuscript map

## Current manuscript

The author-supplied v25 sources are `paper/main.tex`, `paper/sections/` and
`paper/layout.tex`. The PDF has 12 body pages, 13 total pages, seven numbered
sections, 12 figures and five tables. Data and Code Availability is on page 12;
the AI acknowledgment and references start on page 13. Authors are defined in
`paper/authors.tex`. Build/structure records are in `validation/paper_build.json`
and `validation/manuscript_checks.json`.

The [v25 artifact guide](V25_ARTIFACT_GUIDE.md) maps current measurements to
inputs and executable analyses. Historical paper/source snapshots in `archive/`
retain their original bytes and dates.

## Main study: 360 worlds, 720 tasks, 124 configurations

See [STRENGTHENING_GUIDE.md](STRENGTHENING_GUIDE.md) and the
[module README](../experiments/strengthening/README.md).
The October 2 automated study produced 89,280 inference/evaluation records,
720 actual answers and 576 timed requests; eight warm-ups are excluded.
Each phase has a separate completed status record.

`experiments/strengthening/data/strengthening_v1/` contains:

- `corpus.jsonl`, `questions.jsonl`: the public inference boundary, with 720 isolated
  80-chunk searchable collections.
- `truth.jsonl`, `metadata.jsonl`, `claims.jsonl`: world facts, pairing/splits and assertions.
- `specification.json`: generated data dimensions, code, study plan and hashes.
- `audit/`: original parser checks and 60-world packet; author-confirmed human
  completion documentation and detailed review A/B records.

`experiments/runs/strengthening_v1/` contains the 124-configuration manifest,
720 compressed task traces and run status. Each world has two URL-grouping
variants and remains one independent inferential unit.

`experiments/strengthening/results/strengthening_v1/` contains:

| Files | Measurements |
| --- | --- |
| `per_record.csv`, `feasibility.csv`, `status.json` | Delivered-span outcomes, necessary budget bounds and provenance |
| `primary_contrasts.csv`, `exploratory_contrasts.csv`, `subgroup_summary.csv` | World-level primary, exploratory and subgroup statistics |
| `support_flow.csv`, `source_coverage_four_cells.csv` | Stage support and paired endpoint cells |
| `controls.json`, `redundant_support_control.json` | Structural controls |
| `answers/` | 60 test worlds, paired variants, six conditions and 720 original Qwen responses |
| `timing/` | 24 worlds, four configurations, 96 first-pass plus 480 steady requests |
| `analysis.json`, `figures/manifest.json` | Analysis settings and figure/source identities |

The current tables are defined directly in LaTeX. Historical table builders under
`scripts/paper/` write to `build/reanalysis/tables/`, not the current manuscript.

## v25 supplements

All directories below are under `experiments/supplements/`:

- `stage_reanalysis_v1/`: within-question pre/post-cap transitions, packing-input
  versus delivery states, and two exact trace examples.
- `packing_reanalysis_v1/`: restoration, additional losses and all-test complete
  support transitions for alternative packing policies.
- `oncology_coverage_v1/`: final 155 questions, 377 annotated facts, source spans,
  3,100 question-configuration outcomes, stage/fact outcomes and trace provenance.
- `answers_2048_120_v1/`: 240 matched follow-up raw responses, scored records and
  analysis provenance, with an English report companion.

Current Fig. 11(a) uses the final Oncology snapshot: 20 raw-pool misses,
167 packing losses and 2,913 retentions. The historical E3 snapshot below has
20, 171 and 2,909, respectively. Keep those versions separate. Use
`scripts/plot_v25_complementary.py` for the current redraw; the historical redraw
script intentionally reads the older snapshot.

## Frozen original E3: 155 questions by 20 configurations

`experiments/runs/e3_m3/` contains the original manifest, 3,100 per-question
records, all 155 traces, 20-configuration summary, 16 exploratory contrasts,
eight factorial interaction diagnostics and original page-retention heatmap.
These source-informed inputs predate the separately versioned coverage extension.
The table builder outputs to `build/reanalysis/tables/e3/`.
Original integrity results are in `validation/results/e3_integrity.json`;
new verification reports go under `build/verification/e3/`.

## Frozen pilot: 60 worlds, 120 tasks by 20 configurations

Inputs are in `experiments/simulation/data/pilot_v2/`; 120 compressed task traces
are in `experiments/runs/simulation_pilot_v2/`. Open/constrained tasks from one
world are dependent. Results in `experiments/simulation/results/pilot_v2/` include
per-record support/source/conflict outcomes, grouped summaries, budget feasibility,
and `selection.json` with frozen development ties and held-out selection results.
The independent audit is `validation/simulation_audit.json`.

The development complete-coverage tie at 0.600, test outcomes 22/40 and 27/40,
and conditional selected-pair interval remain as reported. This generated pilot
does not supply human E1/E2 utility or an independently collected clinical workload.

## Integrity, reviews and publication

```bash
pixi run --locked strengthen-verify --require-complete
pixi run --locked verify
python scripts/check_world_review_records.py
```

Use `--allow-in-progress` only for an unfinished new run; `PENDING` is not completion.
The dataset semantic-audit completion register records the author's confirmation
of two human approvals. Its original individual forms were not supplied. Saved
review A/B files contain completed dimension-level judgments and evidence indexes. This is separate from the human evidence-utility annotation protocol.

Current repository revisions and dated release assets have separate identities.
The [historical October 13 release](https://github.com/YuZhengYYDS/rerankhurts/releases/tag/icde2027-restructured-20261013)
does not automatically acquire later v25 materials. Public artifact access is
separate from private delivery; repository visibility is unchanged by this update.
