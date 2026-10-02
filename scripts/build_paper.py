"""Build the self-contained manuscript without leaving TeX scratch in paper/."""
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "paper"

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    # Compile a source-only staging tree. Reading a shipped paper/main.bbl while
    # writing a different outdir/main.bbl makes Tectonic repeatedly request a
    # BibTeX rerun. A single working/output directory avoids that ambiguity.
    stage = OUT / "staging"
    stage.mkdir(exist_ok=True)
    for source in (ROOT / "paper").rglob("*"):
        if not source.is_file() or source.name in {"main.pdf", "main.bbl"}:
            continue
        if source.suffix not in {".tex", ".bib", ".cls", ".bst", ".pdf", ".png", ".jpg", ".sty"}:
            continue
        target = stage / source.relative_to(ROOT / "paper")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
    subprocess.run([
        "tectonic", "--keep-logs", "--keep-intermediates",
        "main.tex"
    ], cwd=stage, check=True)
    from pypdf import PdfReader
    pdf = stage / "main.pdf"
    reader = PdfReader(pdf)
    # A conservative check: the whole PDF, including references, fits 12 pages.
    # Longer references are allowed by ICDE but require a main-text boundary audit.
    if len(reader.pages) > 12:
        raise RuntimeError(f"PDF has {len(reader.pages)} pages; audit the main-text boundary before release")
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    if "REPLACE-WITH" in text or "??" in text:
        raise RuntimeError("Unresolved reference or artifact placeholder in PDF")
    shutil.copy2(pdf, ROOT / "paper" / "main.pdf")
    bbl = stage / "main.bbl"
    if bbl.exists():
        shutil.copy2(bbl, ROOT / "paper" / "main.bbl")
    print(f"Built paper/main.pdf ({len(reader.pages)} pages)")

if __name__ == "__main__":
    main()
