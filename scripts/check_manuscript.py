"""Validate the current paragraph-led ICDE draft, without running experiments."""
from pathlib import Path
import hashlib
import json
import re
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"


def balanced_argument(text, start):
    depth = 1
    index = start
    while depth:
        if text[index] == "{" and (index == 0 or text[index - 1] != "\\"):
            depth += 1
        elif text[index] == "}" and (index == 0 or text[index - 1] != "\\"):
            depth -= 1
        index += 1
    return text[start:index - 1]


def main():
    expected = ["A-1"]
    expected += [f"I-{i}" for i in range(1, 6)]
    expected += [f"II-{i}" for i in range(1, 6)]
    expected += [f"III-{i}" for i in range(1, 9)]
    expected += ["IV-0"]
    for group, count in [("A", 3), ("B", 4), ("C", 4), ("D", 8), ("E", 5), ("F", 3)]:
        expected += [f"IV-{group}{i}" for i in range(1, count + 1)]
    expected += [f"V-{i}" for i in range(1, 6)]
    expected += [f"VI-{i}" for i in range(1, 4)] + ["VII-1", "END-1", "END-2"]
    sections = sorted((PAPER / "sections").glob("*.tex"))
    paragraphs = []
    words = 0
    for path in sections:
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"^% P: ([\w-]+)\s*\n\\textbf\{", text, re.M):
            opening = balanced_argument(text, match.end())
            if not opening.rstrip().endswith("."):
                raise RuntimeError(f"Incomplete bold opening: {match.group(1)}")
            paragraphs.append({"id": match.group(1), "file": str(path.relative_to(ROOT)),
                               "opening": opening})
        prose = re.sub(r"(?m)^%.*$", "", text)
        prose = re.sub(r"\\(?:section|subsection|label|ref|cite)\{[^}]*\}", "", prose)
        prose = re.sub(r"\\begin\{equation\}.*?\\end\{equation\}", "", prose, flags=re.S)
        prose = re.sub(r"\\[a-zA-Z]+", "", prose)
        words += len(re.findall(r"\b[A-Za-z]+(?:[-'][A-Za-z]+)*\b", prose))
    if [p["id"] for p in paragraphs] != expected:
        raise RuntimeError("Paragraph IDs or bold openings do not match the 58-paragraph plan")
    source = "\n".join(p.read_text() for p in sections)
    titles = re.findall(r"\\section\{([^}]+)\}", source)
    if len(titles) != 7:
        raise RuntimeError(f"Expected seven numbered sections, found {len(titles)}")
    main_tex = (PAPER / "main.tex").read_text()
    active = main_tex + (PAPER / "layout.tex").read_text() + source
    forbidden = [r"\\vspace\*?\{\s*-", r"\\hspace\*?\{\s*-", r"\\usepackage(?:\[[^]]*\])?\{geometry\}",
                 r"\\(?:addtolength|setlength)\{\\(?:textheight|textwidth|oddsidemargin|topmargin|baselineskip)\}"]
    if any(re.search(pattern, active) for pattern in forbidden):
        raise RuntimeError("Manuscript contains a prohibited geometry/negative-space adjustment")
    if "\\documentclass[conference,10pt,letterpaper]{IEEEtran}" not in main_tex:
        raise RuntimeError("Unexpected conference template settings")
    if re.search(r"\\appendix\b", active):
        raise RuntimeError("Appendix found")
    class_sha = hashlib.sha256((PAPER / "IEEEtran.cls").read_bytes()).hexdigest()
    style_sha = hashlib.sha256((PAPER / "IEEEtran.bst").read_bytes()).hexdigest()
    if class_sha != "da751920a317ed318b7b5cd7fa585a6cc7d28502d457856382e9be24b10a3bd7":
        raise RuntimeError("IEEE class differs from the baseline unmodified official class")
    if style_sha != "314f0ece704568faf827011bac498650691b2b5ee06320720830e782416d5a5f":
        raise RuntimeError("IEEE bibliography style differs from the official baseline")
    stage = Path(json.loads((ROOT / "build/paper/latest_staging.json").read_text())["path"])
    aux = (stage / "main.aux").read_text()
    figures = [{"label": m.group(1), "number": int(m.group(2)), "page": int(m.group(3))}
               for m in re.finditer(r"\\newlabel\{(fig:[^}]+)\}\{\{(\d+)\}\{(\d+)\}", aux)]
    if len(figures) != 12 or [(f["number"], f["page"]) for f in figures] != [(i, i) for i in range(1, 13)]:
        raise RuntimeError(f"Expected one numbered figure on each of 12 pages: {figures}")
    tables = re.findall(r"\\newlabel\{(tab:[^}]+)\}", aux)
    if len(tables) != 4:
        raise RuntimeError("Expected four tables")
    page_check = json.loads((ROOT / "build/paper/page_check.json").read_text())
    pdf = PdfReader(PAPER / "main.pdf")
    if len(pdf.pages) != 12 or page_check["body_pages"] > 12:
        raise RuntimeError("Page budget failed")
    if any(abs(float(page.mediabox.width) - 612) > 0.1 or abs(float(page.mediabox.height) - 792) > 0.1 for page in pdf.pages):
        raise RuntimeError("Unexpected paper size")
    log = (stage / "main.log").read_text(errors="replace")
    if re.search(r"Overfull \\[hv]box|undefined references|Citation .+ undefined", log):
        raise RuntimeError("Overflow or unresolved citation/reference in compilation log")
    report = {"status": "PASS", "paragraph_count": len(paragraphs), "all_openings_bold": True,
              "approximate_english_word_count": words, "numbered_sections": titles,
              "figures": figures, "table_count": len(tables), "page_check": page_check,
              "unmodified_IEEE_class": True, "unmodified_IEEE_bibliography_style": True,
              "intentional_placeholder_figures": [1, 2, 3, 4, 10, 11, 12],
              "submission_ready": False,
              "remaining_items": ["Replace seven intentional figure placeholders", "Provide openly accessible EAB artifacts", "Complete author ORCID/contact/COI submission metadata"],
              "paragraphs": paragraphs}
    target = PAPER / "manuscript_checks.json"
    target.write_text(json.dumps(report, indent=2) + "\n")
    print(f"PASS: {len(paragraphs)} bold openings, 7 sections, 12 pages/figures, 4 tables")


if __name__ == "__main__":
    main()
