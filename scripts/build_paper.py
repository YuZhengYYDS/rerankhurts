"""Build the self-contained manuscript without leaving TeX scratch in paper/."""
from pathlib import Path
import json
import hashlib
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "paper"

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # Compile a source-only staging tree. Reading a shipped paper/main.bbl while
    # writing a different outdir/main.bbl makes Tectonic repeatedly request a
    # BibTeX rerun. A single working/output directory avoids that ambiguity.
    # A fresh directory also prevents a deleted input from surviving in staging.
    stage = Path(tempfile.mkdtemp(prefix="staging-", dir=OUT))
    inputs = {}
    for source in (ROOT / "paper").rglob("*"):
        if not source.is_file() or source.relative_to(ROOT / "paper").as_posix() in {"main.pdf", "main.bbl"}:
            continue
        if source.suffix.casefold() not in {".tex", ".bib", ".cls", ".bst", ".pdf", ".png", ".jpg", ".sty"}:
            continue
        target = stage / source.relative_to(ROOT / "paper")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        inputs[source.relative_to(ROOT / "paper").as_posix()] = file_record(target)
    subprocess.run([
        "tectonic", "--keep-logs", "--keep-intermediates",
        "main.tex"
    ], cwd=stage, check=True)
    from pypdf import PdfReader
    pdf = stage / "main.pdf"
    reader = PdfReader(pdf)
    pages = [page.extract_text() or "" for page in reader.pages]
    # main.tex flushes every float and begins the exempt AI acknowledgment on a
    # new page. ICDE excludes this acknowledgment and the following references.
    source = (stage / "main.tex").read_text(encoding="utf-8")
    boundary = "\\clearpage\n\\section*{Acknowledgment of AI-Generated Content}"
    if boundary not in source:
        raise RuntimeError("An explicit page break before the exempt material is required")
    exempt = [i for i, content in enumerate(pages)
              if "ACKNOWLEDGMENTOFAIGENERATEDCONTENT" in re.sub(r"[^A-Z]", "", content.upper())]
    if len(exempt) != 1:
        raise RuntimeError("Cannot locate the unique AI acknowledgment page")
    body_pages = exempt[0]
    if body_pages > 12:
        raise RuntimeError(f"Manuscript body has {body_pages} pages; ICDE limit is 12")
    text = "\n".join(pages)
    if "REPLACE-WITH" in text or "??" in text:
        raise RuntimeError("Unresolved reference or artifact placeholder in PDF")
    for name, expected in inputs.items():
        if file_record(ROOT / "paper" / name) != expected:
            raise RuntimeError(f"Paper source changed during compilation: {name}")
    shutil.copy2(pdf, ROOT / "paper" / "main.pdf")
    bbl = stage / "main.bbl"
    if bbl.exists():
        shutil.copy2(bbl, ROOT / "paper" / "main.bbl")
    report = {"total_pages": len(reader.pages), "body_pages": body_pages,
              "exempt_material_starts_page": body_pages + 1, "body_page_limit": 12,
              "policy": "https://icde2027.github.io/submission-guidelines.html"}
    (OUT / "page_check.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    identity = {"status": "PASS", "inputs": inputs,
                "outputs": {name: file_record(ROOT / "paper" / name) for name in ("main.pdf", "main.bbl")},
                "page_check": report, "builder_sha256": file_record(Path(__file__))["sha256"]}
    (ROOT / "paper/build_manifest.json").write_text(json.dumps(identity, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "latest_staging.json").write_text(json.dumps({"path": str(stage)}, indent=2) + "\n", encoding="utf-8")
    print(f"Built paper/main.pdf ({body_pages} body pages, {len(reader.pages)} total)")

def file_record(path):
    payload = Path(path).read_bytes()
    return {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}


if __name__ == "__main__":
    main()
