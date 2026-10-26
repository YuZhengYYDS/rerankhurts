"""Recreate historical vector crops under build/, leaving both paper trees unchanged."""
from pathlib import Path
import hashlib
import json
import shutil
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

ROOT = Path(__file__).resolve().parents[1]
ARCHIVED_FIGURES = ROOT / "archive/paper_20261022/figures"
FIGURES = ROOT / "build/reanalysis/paper_20261022/figures"
CROPS = [
    ("support_and_source.pdf", "f05_stages.pdf", (0, 174, 489.6, 360)),
    ("budget_and_mechanisms.pdf", "f07_budgets.pdf", (0, 215, 489.6, 396)),
    ("budget_and_mechanisms.pdf", "f08_heterogeneity.pdf", (0, 0, 489.6, 212)),
    ("answers_and_timing.pdf", "f09_answers.pdf", (0, 185, 489.6, 381.6)),
    ("visibility_packing_policy.pdf", "f06_packing.pdf", (0, 190, 244.8, 367.2)),
    ("visibility_packing_policy.pdf", "f06_dense.pdf", (244.8, 190, 489.6, 367.2)),
    ("visibility_packing_policy.pdf", "f06_ce.pdf", (0, 0, 244.8, 190)),
]


def record(path):
    data = path.read_bytes()
    return {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}


def main():
    if not ARCHIVED_FIGURES.is_dir():
        raise FileNotFoundError(f"Missing frozen archived figures: {ARCHIVED_FIGURES}")
    FIGURES.mkdir(parents=True, exist_ok=True)
    records = []
    for source, target, bounds in CROPS:
        page = PdfReader(ARCHIVED_FIGURES / source).pages[0]
        page.mediabox = RectangleObject(bounds)
        page.cropbox = RectangleObject(bounds)
        writer = PdfWriter()
        writer.add_page(page)
        with (FIGURES / target).open("wb") as stream:
            writer.write(stream)
        records.append({"source": str((ARCHIVED_FIGURES / source).relative_to(ROOT)), "source_identity": record(ARCHIVED_FIGURES / source),
                        "output": f"figures/{target}", "output_identity": record(FIGURES / target),
                        "page": 1, "crop_box_points": bounds})
    concept_names = ["f01_motivation.png", "f02_evidence_views.png", "f03_paired_design.png", "f12_diagnostic_checks.png"]
    plot_names = ["f04_measurement_gap", "f10_request_cost", "f11_complementary_checks"]
    # Copy archived display assets into the scratch inventory; never modify originals.
    display_names = concept_names + [f"{name}.{ext}" for name in plot_names for ext in ("pdf", "svg", "png")]
    for name in display_names + ["concept_provenance.json", "quantitative_provenance.json"]:
        target = FIGURES / name
        if not target.exists():
            shutil.copy2(ARCHIVED_FIGURES / name, target)
    completed = [{"output": f"figures/{name}", "output_identity": record(FIGURES / name),
                  "type": "AI-generated conceptual schematic; no empirical coordinates"} for name in concept_names]
    completed += [{"output": f"figures/{name}.{ext}", "output_identity": record(FIGURES / f"{name}.{ext}"),
                   "type": "Python plot from hash-verified frozen source tables"}
                  for name in plot_names for ext in ("pdf", "svg", "png")]
    manifest = {"scope": "Completed conceptual schematics, source-driven quantitative plots, and reused vector panels; no results inferred from pixels",
                "reused_figure_blocks": [5, 6, 7, 8, 9],
                "intentional_placeholder_figures": [], "completed_assets": completed,
                "concept_provenance": "figures/concept_provenance.json",
                "quantitative_provenance": "figures/quantitative_provenance.json",
                "concept_display_trim_points": {"f02_evidence_views.png": [0, 65, 0, 40],
                                                "f12_diagnostic_checks.png": [0, 80, 0, 140]},
                "trim_scope": "Document display removes outer whitespace only; source PNG bytes unchanged",
                "crops": records}
    (FIGURES.parent / "figure_assets.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Prepared {len(records)} vector crops; all twelve figure blocks complete")


if __name__ == "__main__":
    main()
