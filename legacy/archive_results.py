"""Snapshot a revision round into a date-stamped archive folder.

The experiment pipeline writes everything flat into `result_revision/`, so after
a few rounds there is no way to tell which CSVs, tables and figures a given
paper draft was actually built from -- the file names repeat every round and
only the mtimes differ. This script freezes the current state of a round into

    results_archive/<YYYY-MM-DD_HHMM>_<label>/
        MANIFEST.md      what this round is, what backs which paper draft
        benchmark/       question sets, screening verdicts, validated sets
        raw/             per-mode and per-sweep run outputs (the evidence base)
        tables/          derived summary tables (metrics, analyses, summaries)
        figures/         fig_*.png
        logs/            run logs
        paper_bundle/    copy of what was published into the latex directory

and maintains `results_archive/INDEX.md` (every archive, newest first) plus
`results_archive/LATEST.txt` (path of the newest one).

Nothing is deleted or moved -- the archive is a copy, so the live pipeline in
`result_revision/` keeps working while a round is still running.

Usage:
    python -m legacy.archive_results --label paper-revision --note "P3+P4 rerun"
    python -m legacy.archive_results --dry-run
    python -m legacy.archive_results --from result_revision --exclude-raw
"""
import argparse
import filecmp
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

# The archived copy is what gets released, so the absolute paths a run records
# are normalized here rather than only in future runs.
from legacy.sanitize_release import sanitize_file, sanitize_text

BASE_DIR = Path(__file__).resolve().parents[1]

PAPER_BUNDLE = Path(os.environ.get(
    "PAPER_RESULT_DIR", BASE_DIR / "COLING2027_paper" / "result")).resolve()

BENCHMARK_MARKERS = (
    "questions", "_validated", "screening", "review_final", "judge_sample",
)
TABLE_MARKERS = ("retrieval_metrics_", "analysis_", "paper_table_")
TABLE_SUFFIXES = ("_summary.csv",)

# Files that are inputs rather than products of the round: they belong in the
# archive for reproducibility, but as reference copies, not as "raw results".
CORPUS_MARKERS = ("corpus_chunks", "corpus_manifest", "corpus_stats")

# The corpora and the question sets are inputs the pipeline reads but never
# writes, so they sit next to the scripts rather than in `result_revision/`.
# Scanning only `result_revision/` therefore froze every round without the two
# things a reader needs to reproduce it: which corpus and which question file
# its numbers came from. (The per-run settings CSVs record the file *names*, but
# the files themselves were nowhere in the archive.) Picked up by pattern, since
# they are regenerated under versioned names.
ROOT_INPUT_GLOBS = (
    "corpus_chunks_v*.jsonl",
    "corpus_manifest*.json",
    "corpus_stats*.json",
    "questions*.jsonl",
    "questions_*screening*.csv",
    "questions_expanded_review*.csv",
    "questions_expanded_leakfree_report.csv",
)


def collect_root_inputs() -> List[Path]:
    """The repo-root corpora and question sets that back a round."""
    found: Dict[str, Path] = {}
    for pattern in ROOT_INPUT_GLOBS:
        for path in sorted(BASE_DIR.glob(pattern)):
            if path.is_file():
                found[path.name] = path
    return [found[name] for name in sorted(found)]


# The paper's artifact section promises the corpus construction pipeline, the
# retrieval and re-ranking implementations, and the evaluation scripts. The
# archived CSVs cannot honour that on their own: a reader can see what the
# numbers are but not how they were produced, and the numbers are only
# reproducible if the code that produced them travels with them.
CODE_SUFFIXES = (".py",)
# `README.md` is written for exactly this audience -- how to install, which data
# files are which, and which caveats bind how the numbers may be described -- so
# it travels with the scripts rather than staying behind in the repository.
CODE_FILES = ("legacy/requirements.txt", "legacy/README.md", ".env.example", "README.md")


def collect_code() -> List[Path]:
    """The pipeline's own scripts, frozen with the results they produced."""
    found: Dict[str, Path] = {}
    for path in sorted([*BASE_DIR.glob("*.py"), *(BASE_DIR / "legacy").rglob("*.py")]):
        if path.is_file() and path.suffix in CODE_SUFFIXES:
            found[path.relative_to(BASE_DIR).as_posix()] = path
    for name in CODE_FILES:
        path = BASE_DIR / name
        if path.is_file():
            found[path.relative_to(BASE_DIR).as_posix()] = path
    # `_backup_pre_revision/` is a pre-revision snapshot, not part of the round.
    return [found[name] for name in sorted(found)]


def classify(path: Path) -> str:
    """Route one artifact to its archive subfolder."""
    name = path.name
    low = name.lower()
    if low.endswith(".log"):
        return "logs"
    if low.endswith(".png") or low.endswith(".pdf"):
        return "figures"
    if low.endswith(".jsonl") or any(m in low for m in BENCHMARK_MARKERS):
        return "benchmark"
    if any(m in low for m in CORPUS_MARKERS):
        return "benchmark"
    if any(m in low for m in TABLE_MARKERS) or low.endswith(TABLE_SUFFIXES):
        return "tables"
    if low.endswith(".csv"):
        return "raw"
    return "raw"


def collect(src: Path, exclude_raw: bool) -> Dict[str, List[Path]]:
    groups: Dict[str, List[Path]] = {
        "benchmark": [], "raw": [], "tables": [], "figures": [], "logs": [],
        "code": [],
    }
    for path in sorted(src.iterdir()):
        if not path.is_file():
            continue
        if exclude_raw and path.suffix.lower() == ".csv" and classify(path) == "raw":
            continue
        groups[classify(path)].append(path)
    return groups


def human(nbytes: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if nbytes < 1024 or unit == "GB":
            return f"{nbytes:.1f} {unit}" if unit != "B" else f"{nbytes} B"
        nbytes /= 1024.0
    return f"{nbytes:.1f} GB"


def copy_group(paths: List[Path], dest: Path, preserve_code_paths: bool = False) -> List[Tuple[str, int]]:
    dest.mkdir(parents=True, exist_ok=True)
    written = []
    for p in paths:
        relative = p.relative_to(BASE_DIR) if preserve_code_paths else Path(p.name)
        target = dest / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        # The archive is the released copy, so this machine's directory layout is
        # stripped from it on the way in (see sanitize_release.py). Sanitizing
        # happens on the copy, never in place: the working copy in
        # `result_revision/` stays byte-for-byte what the run wrote.
        is_csv = target.suffix.lower() == ".csv"
        # Re-copy only when the content actually differs, so a re-archive of an
        # unchanged round does not churn mtimes. For CSVs the comparison is
        # against the sanitized form, since that is what the target holds.
        if target.exists():
            if is_csv:
                try:
                    same = (target.read_text(encoding="utf-8-sig")
                            == sanitize_text(p.read_text(encoding="utf-8-sig")))
                except (UnicodeDecodeError, OSError):
                    same = filecmp.cmp(p, target, shallow=False)
            else:
                same = filecmp.cmp(p, target, shallow=False)
            if same:
                written.append((relative.as_posix(), target.stat().st_size))
                continue
        shutil.copy2(p, target)
        if is_csv:
            sanitize_file(target)
        written.append((relative.as_posix(), target.stat().st_size))
    return written


def copy_derived_evals(src: Path, dest: Path) -> Dict[str, List[str]]:
    """Freeze the per-view evaluation folders (`newrr_eval/`, `p4_eval/`, ...).

    `paper_support_analysis.py` is run more than once with a different
    `RESULTS_FILE` / `ANALYSIS_PREFIX` and writes each view into its own
    subdirectory. Those views are not decorative: the re-ranker table's
    delta/p columns on the 78-question set come from
    `newrr_eval/newrr_pairwise_vs_baseline.csv`, its expanded-benchmark columns
    come from `p4_eval/p4_pairwise_vs_baseline.csv`, and the right panel of the
    stage-retention figure is drawn from
    `newrr_eval/newrr_stage_gold_retention.csv`. Archiving only the top-level
    CSVs left the evidence for the paper's central new table outside the frozen
    round, so a later reader could not check it against the run it came from.

    Each view keeps its own subdirectory (their file names collide with the
    top-level ones), copied whole so nothing in a view is silently dropped.
    """
    copied: Dict[str, List[str]] = {}
    for view in sorted(p for p in src.glob("*_eval") if p.is_dir()):
        files = sorted(f for f in view.iterdir() if f.is_file())
        if not files:
            continue
        target_dir = dest / view.name
        target_dir.mkdir(parents=True, exist_ok=True)
        names = []
        for f in files:
            target = target_dir / f.name
            if not (target.exists() and filecmp.cmp(f, target, shallow=False)):
                shutil.copy2(f, target)
            names.append(f.name)
        copied[view.name] = names
    return copied


def headline_numbers(src: Path) -> str:
    """Pull the main retrieval table so the manifest states the actual results."""
    cand = src / "retrieval_metrics_overall.csv"
    if not cand.exists():
        return "_No `retrieval_metrics_overall.csv` in this round yet._\n"
    try:
        import pandas as pd
        df = pd.read_csv(cand)
    except Exception as exc:  # pragma: no cover - diagnostic path
        return f"_Could not read retrieval metrics: {exc}_\n"
    cols = [c for c in ["mode", "num_questions", "recall_at_5", "recall_at_10",
                        "mrr", "ndcg_at_10"] if c in df.columns]
    lines = ["| " + " | ".join(cols) + " |",
             "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df[cols].iterrows():
        cells = []
        for c in cols:
            v = r[c]
            cells.append(f"{v:.4f}" if isinstance(v, float) else str(v))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def write_manifest(arch: Path, src: Path, label: str, note: str,
                   groups: Dict[str, List[Path]], copied: Dict[str, List[Tuple[str, int]]],
                   stamp: str, derived: Dict[str, List[str]] | None = None) -> None:
    total = sum(sz for files in copied.values() for _, sz in files)
    lines = [
        f"# Results archive — {stamp} — {label}",
        "",
        f"- **Archived:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Source directory:** `{src.name}/`",
        f"- **Label:** `{label}`",
        f"- **Total size:** {human(total)} "
        f"({sum(len(v) for v in copied.values())} files)",
        "",
    ]
    if note:
        lines += ["## What this round is", "", note.strip(), ""]

    lines += ["## Headline retrieval numbers", "", headline_numbers(src).rstrip(), ""]

    lines += ["## Contents", "",
              "| Folder | Files | Size | What it holds |",
              "|---|---|---|---|",
              "| `benchmark/` | {n} | {s} | question sets, screening verdicts, validated sets |".format(
                  n=len(copied["benchmark"]),
                  s=human(sum(sz for _, sz in copied["benchmark"]))),
              "| `raw/` | {n} | {s} | per-mode and per-sweep run outputs (evidence base) |".format(
                  n=len(copied["raw"]),
                  s=human(sum(sz for _, sz in copied["raw"]))),
              "| `tables/` | {n} | {s} | derived summary tables |".format(
                  n=len(copied["tables"]),
                  s=human(sum(sz for _, sz in copied["tables"]))),
              "| `figures/` | {n} | {s} | figures |".format(
                  n=len(copied["figures"]),
                  s=human(sum(sz for _, sz in copied["figures"]))),
              "| `logs/` | {n} | {s} | run logs |".format(
                  n=len(copied["logs"]),
                  s=human(sum(sz for _, sz in copied["logs"]))),
              "| `code/` | {n} | {s} | the pipeline that produced these numbers |".format(
                  n=len(copied["code"]),
                  s=human(sum(sz for _, sz in copied["code"]))),
              "| `paper_bundle/` | see below | | what was copied into the latex dir |",
              ""]

    for group in ("benchmark", "tables", "figures"):
        if not copied[group]:
            continue
        lines += [f"### {group}/", ""]
        if group == "benchmark":
            lines += ["The corpora and question sets listed here are copied from the "
                      "repository root: they are inputs the pipeline reads but never "
                      "writes, so they are not products of this round. Without them a "
                      "reader cannot tell which corpus or question file the numbers "
                      "below came from, nor re-run anything.", ""]
        lines += [f"- `{name}`" for name, _ in sorted(copied[group])]
        lines.append("")

    if copied["raw"]:
        lines += ["### raw/", "",
                  f"{len(copied['raw'])} run outputs; the per-mode files for one batch "
                  f"share a `<stem>_<mode>.csv` prefix and are combined by "
                  f"`combine_revision_results.py`.", ""]

    if copied["code"]:
        lines += ["### code/", "",
                  "The scripts, frozen as they were at the moment these results were "
                  "produced. A later edit to the pipeline does not retroactively "
                  "change what this round did, and the numbers above are only "
                  "checkable against the code that wrote them.", "",
                  "`requirements.txt` and `.env.example` travel with them because "
                  "the scripts will not run without the dependencies or the endpoint "
                  "configuration; see `.env.example` for what to set.", ""]
        lines += [f"- `{name}`" for name, _ in sorted(copied["code"])]
        lines.append("")

    if derived:
        lines += ["### tables/<view>_eval/", "",
                  "Per-view `paper_support_analysis.py` runs. The re-ranker table "
                  "and the stage-retention figure are computed from these, not "
                  "from the top-level tables.", ""]
        for view, names in sorted(derived.items()):
            lines += [f"- `tables/{view}/` ({len(names)} files)", ""]

    if (arch / "paper_bundle").exists():
        bundle_files = sorted(p.name for p in (arch / "paper_bundle").iterdir() if p.is_file())
        lines += ["### paper_bundle/", "",
                  "Files published into "
                  "`COLING2027_paper/result/` for this round:", ""]
        lines += [f"- `{n}`" for n in bundle_files]
        lines.append("")

    lines += ["## How to regenerate", "",
              "```",
              "python -m legacy.build_revision_assets --publish",
              "```",
              "",
              "That chain is: `combine_revision_results.py` -> `score_retrieval.py` -> "
              "`analyze_results.py` -> `make_figures.py` -> `make_heatmaps.py` -> "
              "`paper_support_analysis.py` -> `summarize_supplement_results.py` -> "
              "`make_revision_tables.py` -> `curate_paper_assets.py` -> publish.",
              "",
              "The per-view tables under `tables/*_eval/` come from separate "
              "`paper_support_analysis.py` runs over their own result files (the "
              "re-ranker family on the 78-question set, and the expanded "
              "155-question benchmark). Each is pointed at its view directory with "
              "`RESULT_DIR` and named with `ANALYSIS_PREFIX`; they are not part of "
              "the chain above because they read result files the chain does not "
              "produce.",
              ""]
    (arch / "MANIFEST.md").write_text("\n".join(lines), encoding="utf-8")


README = """# Results archive

Every completed rebuild round is frozen here as `results_archive/<date>_<time>_<label>/`.
Newest first in `INDEX.md`; `LATEST.txt` always points at the newest one.

## Why this exists

The live pipeline writes every run into `result_revision/` under file names that
repeat each round (`retrieval_metrics_overall.csv`, `fig_main_retrieval.png`, ...),
so after two rounds only mtimes distinguish them. Freezing each round by
timestamp is what makes "which numbers does the paper draft actually use"
answerable later.

## How the result folders relate

| Folder | Role |
|---|---|
| `result/` | The original submission's runs. Kept read-only as the pre-revision reference (`paper_questions_validated.jsonl` lives here). |
| `result_revision/` | The **live** working directory. Experiments overwrite files here while a round is in progress -- treat it as scratch, not as a record. |
| `results_archive/` | **Frozen rounds.** One folder per completed rebuild; nothing here is ever overwritten. |
| `COLING2027_paper/result/` | What the current paper consumes. Its `PROVENANCE.md` names the archive folder the shipped figures came from. |

## Inside one archive

| Folder | Contents |
|---|---|
| `MANIFEST.md` | What the round is, its headline retrieval numbers, full file inventory |
| `benchmark/` | Question sets, screening verdicts, validated sets, corpus inputs |
| `raw/` | Per-mode and per-sweep run outputs -- the evidence base for every table |
| `tables/` | Derived metrics and summaries |
| `figures/` | `fig_*.png` |
| `logs/` | Run logs |
| `code/` | The pipeline scripts and `requirements.txt` / `.env.example`, as they were when the round ran |
| `paper_bundle/` | Snapshot of what was published into the latex directory |

## Reproducing a round

```bash
python -m legacy.build_revision_assets --publish --archive-note "<what changed>"
```
"""


def ensure_readme(root: Path) -> None:
    """Write the layout explainer once; never clobber a hand-edited version."""
    readme = root / "README.md"
    if not readme.exists():
        readme.write_text(README, encoding="utf-8")


def mark_superseded(root: Path, arch: Path, label: str) -> List[str]:
    """Flag earlier archives of the same label as replaced by `arch`.

    Re-running the same round (same label, later stamp) would otherwise leave
    two folders that look equally current -- and the older one still holds the
    figures from before whatever fix prompted the re-run. Nothing is deleted;
    the earlier folders get a `SUPERSEDED.md` and an index marker instead.
    """
    superseded = []
    for old in sorted(root.iterdir()):
        if not old.is_dir() or old.name == arch.name:
            continue
        if not (old.name.endswith(f"_{label}") or f"_{label}" in old.name):
            continue
        (old / "SUPERSEDED.md").write_text(
            f"# Superseded\n\n"
            f"This round was replaced by `{arch.name}`.\n\n"
            f"Both folders were rebuilt from the same working directory and carry "
            f"the same label, so `{arch.name}` is the one to cite. The figures and "
            f"tables here predate the rebuild that produced it -- do not mix "
            f"numbers between the two.\n",
            encoding="utf-8",
        )
        superseded.append(old.name)
    return superseded


def update_index(root: Path, arch: Path, label: str, note: str) -> None:
    """Prepend this archive to INDEX.md and repoint LATEST.txt."""
    superseded = mark_superseded(root, arch, label)

    entries = []
    index = root / "INDEX.md"
    if index.exists():
        entries = index.read_text(encoding="utf-8").splitlines()
        # Drop the header block; keep only previous bullet lines.
        entries = [ln for ln in entries if ln.startswith("- ")]
        # Re-derive rather than append, so refreshing the index (or re-running
        # the driver) does not stack duplicate bullets or superseded markers.
        marked = []
        for ln in entries:
            ln = re.sub(r" \*\*\(superseded by [^)]*\)\*\*", "", ln)
            name = ln.split("**")[1] if ln.count("**") >= 2 else ""
            if name == arch.name:
                continue
            if name in superseded:
                ln += f" **(superseded by {arch.name})**"
            marked.append(ln)
        entries = marked

    bullet = f"- **{arch.name}** — {label}" + (f" — {note.splitlines()[0]}" if note else "")
    entries = [bullet] + entries

    body = ["# Results archive index", "",
            "Newest first. Each folder holds one frozen round; see its `MANIFEST.md` "
            "for what the numbers are and which paper draft they back.", ""]
    body += entries
    body.append("")
    index.write_text("\n".join(body), encoding="utf-8")

    (root / "LATEST.txt").write_text(
        f"{arch.name}\n\nFull path: {arch}\nArchived: "
        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="src", default="result_revision",
                    help="Working directory to snapshot (default: result_revision)")
    ap.add_argument("--root", default="results_archive",
                    help="Archive root (default: results_archive)")
    ap.add_argument("--label", default="revision", help="Short round label")
    ap.add_argument("--note", default="", help="Free text: what this round is")
    ap.add_argument("--exclude-raw", action="store_true",
                    help="Skip the per-mode raw CSVs (keeps the archive small)")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--stamp", default=None,
                    help="Override the timestamp (for re-runs of the same round)")
    args = ap.parse_args()

    src = BASE_DIR / args.src
    if not src.is_dir():
        raise SystemExit(f"Source directory not found: {src}")
    root = BASE_DIR / args.root

    stamp = args.stamp or datetime.now().strftime("%Y-%m-%d_%H%M")
    arch = root / f"{stamp}_{args.label}"

    groups = collect(src, args.exclude_raw)
    root_inputs = collect_root_inputs()
    archived_names = {p.name for p in groups["benchmark"]}
    groups["benchmark"].extend(p for p in root_inputs if p.name not in archived_names)
    groups["benchmark"].sort(key=lambda p: p.name)
    groups["code"] = collect_code()
    total_files = sum(len(v) for v in groups.values())

    print(f"Source : {src}")
    print(f"Archive: {arch}")
    for name, paths in groups.items():
        print(f"  {name:10s} {len(paths):4d} files")
    print(f"  {'TOTAL':10s} {total_files:4d} files")
    print(f"  (of which {len(root_inputs)} are repo-root corpora/question sets)")

    if args.dry_run:
        print("\n(dry run -- nothing written)")
        return

    arch.mkdir(parents=True, exist_ok=True)
    ensure_readme(root)
    copied = {name: copy_group(paths, arch / name, preserve_code_paths=name == "code")
              for name, paths in groups.items()}

    if PAPER_BUNDLE.is_dir():
        copy_group(sorted(p for p in PAPER_BUNDLE.iterdir() if p.is_file()),
                   arch / "paper_bundle")
    else:
        print(f"  !! paper bundle not found: {PAPER_BUNDLE}")

    derived: Dict[str, List[str]] = {}
    if not args.exclude_raw:
        derived = copy_derived_evals(src, arch / "tables")
        for view, names in sorted(derived.items()):
            print(f"  tables/{view}: {len(names)} files")

    write_manifest(arch, src, args.label, args.note, groups, copied, stamp, derived)
    update_index(root, arch, args.label, args.note)

    size = sum(sz for files in copied.values() for _, sz in files)
    print(f"\nArchived {total_files} files ({human(size)}) -> {arch}")
    print(f"Index   : {root / 'INDEX.md'}")
    print(f"Latest  : {root / 'LATEST.txt'}")


if __name__ == "__main__":
    main()
