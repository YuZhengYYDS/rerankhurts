# Historical source snapshots

`paper_20261022/` preserves the complete manuscript tree from commit `c67d4dfe89e338c2ba93f6e3001580beaa8044f5`, including editable draw.io figures, the supplied SVG catalog, figure source data, build helpers and provenance. The current source project is `../paper/`; its revised Figures 4–12 use the supplied `-v2.pdf` assets.

`code_20261022/` preserves the five Python scripts formerly stored at the repository root. These snapshots retain their original bytes for frozen input-manifest checks. Maintained tools are in `../legacy/`; invoke those through `python -m rerankhuts legacy-*` or their `python -m legacy.<module>` entry points from the repository root.

Archived scripts are provenance records, not maintained entry points. Current build and historical figure/table reanalysis helpers live under `../scripts/`, with generated scratch and reanalysis outputs under `../build/`. Do not edit frozen snapshots to update the active manuscript or bypass a recorded source hash.
