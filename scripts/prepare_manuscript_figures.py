"""Crop existing vector panels for the argument-led draft; do not redraw data."""
from pathlib import Path
import hashlib
import json
from pypdf import PdfReader, PdfWriter
from pypdf.generic import RectangleObject

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "paper/figures"
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
    records = []
    for source, target, bounds in CROPS:
        page = PdfReader(FIGURES / source).pages[0]
        page.mediabox = RectangleObject(bounds)
        page.cropbox = RectangleObject(bounds)
        writer = PdfWriter()
        writer.add_page(page)
        with (FIGURES / target).open("wb") as stream:
            writer.write(stream)
        records.append({"source": f"figures/{source}", "source_identity": record(FIGURES / source),
                        "output": f"figures/{target}", "output_identity": record(FIGURES / target),
                        "page": 1, "crop_box_points": bounds})
    manifest = {"scope": "Vector cropping of existing plots; no data were redrawn or inferred from pixels",
                "reused_figure_blocks": [5, 6, 7, 8, 9],
                "intentional_placeholder_figures": [1, 2, 3, 4, 10, 11, 12],
                "placeholder_location": "layout.tex", "crops": records}
    (ROOT / "paper/figure_assets.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Prepared {len(records)} vector crops; seven figure placeholders remain")


if __name__ == "__main__":
    main()
