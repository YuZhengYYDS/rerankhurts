"""Build the manuscript, keeping compiler scratch and audit records outside paper/."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "build" / "paper"
INPUT_SUFFIXES = {".tex", ".bib", ".cls", ".bst", ".pdf", ".png", ".jpg", ".sty"}


def file_record(path):
    payload = Path(path).read_bytes()
    return {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}


def compiler_commands(engine="auto", tectonic=None):
    """Prefer the supplied PDFLaTeX/BibTeX workflow; allow a portable fallback."""
    pdflatex, bibtex = shutil.which("pdflatex"), shutil.which("bibtex")
    if engine in {"auto", "pdflatex"} and pdflatex and bibtex:
        latex = [pdflatex, "-interaction=nonstopmode", "-halt-on-error", "main.tex"]
        return "pdflatex", [latex, [bibtex, "main"], latex, latex]
    if engine == "pdflatex":
        raise RuntimeError("PDFLaTeX and BibTeX must both be available on PATH")
    binary = tectonic or os.environ.get("TECTONIC") or shutil.which("tectonic")
    if not binary:
        raise RuntimeError("Install PDFLaTeX/BibTeX or Tectonic; alternatively pass --tectonic PATH")
    return "tectonic", [[str(binary), "--keep-logs", "--keep-intermediates", "main.tex"]]


def page_report(stage):
    from pypdf import PdfReader

    reader = PdfReader(stage / "main.pdf")
    pages = [page.extract_text() or "" for page in reader.pages]
    aux = (stage / "main.aux").read_text(encoding="utf-8")
    boundary = re.search(r"\\newlabel\{bodyend\}\{\{[^}]*\}\{(\d+)\}", aux)
    if boundary is None:
        raise RuntimeError("Cannot locate the final body-page label")
    exempt = [i for i, content in enumerate(pages)
              if "ACKNOWLEDGMENTOFAIGENERATEDCONTENT" in re.sub(r"[^A-Z]", "", content.upper())]
    if len(exempt) != 1:
        raise RuntimeError("Cannot locate the unique AI acknowledgment page")
    last_body_text_page = int(boundary.group(1))
    body_float_pages = [int(m.group(1)) for m in re.finditer(
        r"\\newlabel\{(?:fig|tab):[^}]+\}\{\{[^}]*\}\{(\d+)\}", aux)]
    body_pages = max([last_body_text_page, *body_float_pages])
    if body_pages > 12:
        raise RuntimeError(f"Manuscript body has {body_pages} pages; ICDE limit is 12")
    if "REPLACE-WITH" in "\n".join(pages) or "??" in "\n".join(pages):
        raise RuntimeError("Unresolved reference or artifact placeholder in PDF")
    return {"total_pages": len(reader.pages), "body_pages": body_pages,
            "exempt_material_starts_page": exempt[0] + 1, "body_page_limit": 12,
            "body_count_method": "last body label plus numbered body floats; shared exempt/body pages count as body",
            "last_body_text_page": last_body_text_page,
            "body_float_pages": sorted(set(body_float_pages)),
            "policy": "https://icde2027.github.io/submission-guidelines.html"}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compiler", choices=("auto", "pdflatex", "tectonic"), default="auto")
    parser.add_argument("--tectonic", type=Path, help="Tectonic executable when it is not on PATH")
    args = parser.parse_args(argv)
    engine, commands = compiler_commands(args.compiler, args.tectonic)
    OUT.mkdir(parents=True, exist_ok=True)
    # Fresh staging prevents deleted sources and a shipped .bbl from surviving.
    stage = Path(tempfile.mkdtemp(prefix="staging-", dir=OUT))
    inputs = {}
    for source in (ROOT / "paper").rglob("*"):
        relative = source.relative_to(ROOT / "paper").as_posix()
        if not source.is_file() or relative in {"main.pdf", "main.bbl"}:
            continue
        if source.suffix.casefold() not in INPUT_SUFFIXES:
            continue
        target = stage / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        inputs[relative] = file_record(target)
    for command in commands:
        subprocess.run(command, cwd=stage, check=True)
    report = page_report(stage)
    log = (stage / "main.log").read_text(errors="replace")
    if re.search(r"undefined references|Citation .+ undefined", log):
        raise RuntimeError("Unresolved citation/reference in compilation log")
    for name, expected in inputs.items():
        if file_record(ROOT / "paper" / name) != expected:
            raise RuntimeError(f"Paper source changed during compilation: {name}")
    shutil.copy2(stage / "main.pdf", ROOT / "paper" / "main.pdf")
    (OUT / "page_check.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    version = subprocess.run([commands[0][0], "--version"], check=True,
                             capture_output=True, text=True).stdout.splitlines()[0]
    identity = {"schema_version": 2, "status": "PASS", "paper_root": "paper",
                "inputs": inputs, "outputs": {"main.pdf": file_record(ROOT / "paper/main.pdf")},
                "page_check": report, "builder_sha256": file_record(Path(__file__))["sha256"],
                "compiler": {"engine": engine, "version": version,
                             "commands": [[Path(command[0]).name, *command[1:]] for command in commands]}}
    validation = ROOT / "validation"
    validation.mkdir(exist_ok=True)
    (validation / "paper_build.json").write_text(json.dumps(identity, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    (OUT / "latest_staging.json").write_text(json.dumps({"path": str(stage)}, indent=2) + "\n", encoding="utf-8")
    print(f"Built paper/main.pdf ({report['body_pages']} body pages, {report['total_pages']} total; {engine})")
    return identity


if __name__ == "__main__":
    main()
