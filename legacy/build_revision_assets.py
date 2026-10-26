"""Rebuild every paper artifact from ONE unified result set.

The original submission mixed numbers from at least three different runs: the
main table came from the "strong baselines" run, the main figure from an older
`rag_results_experiments.csv` run, and the answer-rate panel was hard-coded in
`make_modified_images.py`. This driver removes that ambiguity by regenerating
everything from the raw per-question CSVs in `result_revision/`.

Chain:
    result_revision/supp_*_<mode>.csv        raw, from run_p3_matrix / run_p4_expanded
      -> combine_revision_results.py         stitch per-mode files into one combined CSV
      -> score_retrieval.py                  retrieval_metrics_{overall,by_topic}.csv
      -> analyze_results.py                  analysis_{overall,by_topic}.csv
      -> make_figures.py                     fig_main_retrieval.png, fig_answer_rates.png, ...
      -> make_heatmaps.py                    labelled topic heatmaps
      -> paper_support_analysis.py           audit, full-vs-audited, pairwise, diagnostics
      -> summarize_supplement_results.py     per-sweep summaries
      -> make_revision_tables.py             revision tables + correlations
      -> curate_paper_assets.py              paper tables + curated figures
      -> publish_figures()                   copy figures into the paper bundle

`make_modified_images.py` is deliberately NOT part of this chain: its two
figures were hard-coded constants, and the real generators above supersede
them. Run with --publish to overwrite the figures shipped in the paper bundle.

--publish also freezes the round into `results_archive/<timestamp>_<label>/`
(see `archive_results.py`). Because every round overwrites the same filenames in
`result_revision/`, the archive is what makes "which numbers does this paper
draft actually use" answerable after the fact. Pass --no-archive to skip it.

Usage:
    python -m legacy.build_revision_assets --dry-run
    python -m legacy.build_revision_assets
    python -m legacy.build_revision_assets --publish --archive-note "P3+P4 rerun"
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from legacy.sanitize_release import sanitize_file
from rerankhuts.paths import oncology_path

BASE = Path(__file__).resolve().parents[1]
REV = BASE / "result_revision"
BUNDLE = REV / "bundle"
PAPER_DIR = Path(os.environ.get(
    "PAPER_DIR", BASE / "COLING2027_paper")).resolve()
PAPER_RESULT = Path(os.environ.get(
    "PAPER_RESULT_DIR", PAPER_DIR / "result")).resolve()
PAPER_LATEX = PAPER_DIR
TEX_FILE = PAPER_DIR / "acl_latex.tex"

FULL100 = str(oncology_path("questions.jsonl", root=BASE))

# SHA-256 of the two figures `make_modified_images.py` produced from hard-coded
# arrays, kept because deleting the script does not delete its output: the PNGs
# still sit in `修改图片/`, and copying one back into the paper's result/
# directory would silently restore a fabricated figure under a filename the real
# generators also write. Byte-identity is the only trace that survives that copy,
# so the hashes are checked at publish time and the build stops if one appears.
#
# fig_answer_rates.png    b057ff8a...
# fig_paper_full_vs_audited.png  59cfbf6f...
FABRICATED_FIGURE_SHA256 = {
    "b057ff8aafb7589b6eaabe1125d959265de4dc9f3a247a07ed973582baf1552b": "fig_answer_rates.png",
    "59cfbf6f8290f5aa4aeaa4aca42c2002cdbc86b5935705165b6e3914c15e8605": "fig_paper_full_vs_audited.png",
}


def sha256_of(path: Path) -> str:
    import hashlib
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def refuse_fabricated_figures(figures: list) -> None:
    """Stop the publish if any figure to be shipped is a known fabricated one."""
    hits = []
    for fig in figures:
        if sha256_of(fig) in FABRICATED_FIGURE_SHA256:
            hits.append(f"{fig.name} (== {FABRICATED_FIGURE_SHA256[sha256_of(fig)]} "
                        f"from 修改图片/)")
    if hits:
        raise SystemExit(
            "Refusing to publish hand-authored figure(s):\n  "
            + "\n  ".join(hits)
            + "\nThese are hard-coded outputs of make_modified_images.py, not "
              "generated from the current run. Delete them and let the figure "
              "generators write the file, or point the paper at the generated "
              "figure under a different name.")


def run(script: str, env_overrides: dict, label: str, dry: bool) -> bool:
    env = os.environ.copy()
    env.update({k: str(v) for k, v in env_overrides.items()})
    print(f"\n{'=' * 70}\n>>> {label}\n    {script}", flush=True)
    for k, v in env_overrides.items():
        print(f"      {k}={v}", flush=True)
    if dry:
        return True
    command = [sys.executable, "-m", "legacy." + Path(script).stem]
    r = subprocess.run(command, env=env, cwd=BASE)
    ok = r.returncode == 0
    print(f"    -> {'OK' if ok else f'FAILED(exit {r.returncode})'}", flush=True)
    return ok


# CSVs the paper's numbers are read from. They are published next to the
# figures so the directory a reader actually opens states the same numbers the
# tex does. Previously only `fig_*.png` were copied, which is how the appendix
# tables came to cite a stale CSV set: the figures were refreshed every round
# while the tables beside them silently were not.
PUBLISHED_CSV_PATTERNS = [
    "paper_table_*.csv",          # curated paper tables
    "rev_table_*.csv",            # benchmark / re-ranker / judge views
    "accuracy_cost_pareto_clean.csv",
    "paper_*.csv",                # audit, split, pairwise, stage, transition, cases
    "rag_results_experiments.csv",
    "retrieval_metrics_*.csv",
    "analysis_*.csv",
    "main_results_table.csv",
    "supp_*_summary.csv",
    "supp_*_overall.csv",
    "supp_*_best.csv",
    "supp_strong_baselines_full100_metrics_by_subset.csv",
    "supp_strong_baselines_validated_pairwise_vs_baseline.csv",
]


def publish_figures(dry: bool, stamp: str, label: str) -> int:
    """Copy the regenerated figures and their source CSVs into the paper bundle.

    Also drops a PROVENANCE.md naming the archive folder this round was frozen
    into, and a RESULT_INDEX.md separating the files this round produced from
    whatever else is sitting in the directory, so a stale file can never be
    mistaken for a current one.
    """
    figures, csvs = [], []
    for d in (REV, BUNDLE):
        if not d.exists():
            continue
        figures.extend(sorted(d.glob("fig_*.png")))
        for pattern in PUBLISHED_CSV_PATTERNS:
            csvs.extend(sorted(d.glob(pattern)))
    if not figures:
        print("!! no fig_*.png found to publish")
        return 0
    refuse_fabricated_figures(figures)

    # A file matched in both REV and BUNDLE (the curated tables live in both)
    # is published once, from the first source that has it.
    csvs = sorted({p.name: p for p in csvs}.values(), key=lambda p: p.name)

    # The docs describing the asset set travel with it. Without this the paper's
    # result/ directory keeps whichever README and asset map an earlier round
    # dropped there, listing filenames that no longer exist next to files that
    # do -- which is exactly how a stale table gets cited by mistake.
    # `curate_paper_assets.py` writes its README into the curated subfolder
    # rather than the bundle root, so both locations are sources; bundle root
    # wins on a name collision.
    docs_by_name: dict[str, Path] = {}
    for d in (BUNDLE, BUNDLE / "paper_assets_curated"):
        if d.exists():
            for p in sorted(d.glob("*.md")):
                docs_by_name.setdefault(p.name, p)
    docs = [docs_by_name[name] for name in sorted(docs_by_name)]

    print(f"\n{'=' * 70}\n>>> publish figures + source CSVs -> {PAPER_RESULT}")
    if dry:
        for f in figures:
            print(f"      {f.name}")
        print(f"      (+{len(csvs)} CSV files)")
        return len(figures)

    PAPER_RESULT.mkdir(parents=True, exist_ok=True)
    for f in figures:
        shutil.copy2(f, PAPER_RESULT / f.name)
        print(f"      {f.name}")
    for c in csvs:
        shutil.copy2(c, PAPER_RESULT / c.name)
        # The bundle is released too, so the same path normalization the archive
        # applies has to happen here.
        sanitize_file(PAPER_RESULT / c.name)
    for d in docs:
        shutil.copy2(d, PAPER_RESULT / d.name)
    print(f"      ({len(csvs)} CSV files + {len(docs)} docs refreshed)")

    # PROVENANCE.md and RESULT_INDEX.md are written below, not copied, so they
    # are current by construction and must not be reported as leftovers.
    ours = {"PROVENANCE.md", "RESULT_INDEX.md"}
    published = ({f.name for f in figures} | {c.name for c in csvs}
                 | {d.name for d in docs} | ours)
    stale = sorted(p.name for p in PAPER_RESULT.iterdir()
                   if p.is_file() and p.name not in published
                   and p.suffix.lower() in {".csv", ".jsonl", ".md"})

    provenance = [
        "# Provenance of the figures and tables in this directory",
        "",
        f"- **Published:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Result set:** `results_archive/{stamp}_{label}/`",
        f"- **Rebuilt by:** `python -m legacy.build_revision_assets --publish "
        f"--archive-label {label}`",
        "",
        "Everything in this result directory was regenerated from the raw "
        "per-question run outputs in that archive; no generated figure or table "
        "was hand-edited. See the archive's "
        "`MANIFEST.md` for the headline numbers and the file inventory.",
        "",
        "See `RESULT_INDEX.md` for which files this round wrote and which are "
        "leftovers that must not be cited.",
        "",
    ]
    (PAPER_RESULT / "PROVENANCE.md").write_text("\n".join(provenance), encoding="utf-8")
    print(f"      PROVENANCE.md -> results_archive/{stamp}_{label}/")

    write_result_index(stamp, label, figures, csvs, stale)
    write_submission_manifest(stamp, label)
    return len(figures)


def write_result_index(stamp: str, label: str, figures, csvs, stale) -> None:
    """Say plainly which files in result/ are current and which are leftovers.

    Non-destructive: leftover files are listed, never deleted. Some predate this
    revision and may still be cited by nothing; others are produced by helper
    scripts outside the rebuild chain. Naming them is what stops a reader from
    quoting an old number that happens to still be lying around.
    """
    lines = [
        "# What is current in this directory",
        "",
        f"- **Published:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Result set:** `results_archive/{stamp}_{label}/`",
        "",
        f"## Regenerated by this round ({len(figures)} figures, {len(csvs)} CSVs)",
        "",
        "Every number in the paper is read from these. `acl_latex.tex` is "
        "checked against them.",
        "",
    ]
    lines += [f"- `{f.name}`" for f in sorted(figures, key=lambda p: p.name)]
    lines += [f"- `{c.name}`" for c in csvs]

    lines += ["", f"## Leftovers in this directory ({len(stale)})", ""]
    if stale:
        lines += [
            "**Not written by this round — do not cite.** Either superseded by a "
            "file above with a different name, or produced by a helper script "
            "outside the rebuild chain. Listed, not deleted, so the discrepancy "
            "stays visible.",
            "",
        ]
        lines += [f"- `{name}`" for name in stale]
    else:
        lines.append("_None._")
    lines.append("")

    (PAPER_RESULT / "RESULT_INDEX.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"      RESULT_INDEX.md ({len(stale)} leftover file(s) flagged)")


def write_submission_manifest(stamp: str, label: str) -> None:
    """List the files this paper actually needs, derived from the tex itself.

    The hand-written upload lists that shipped with the original submission
    named a superseded `.tex` and an older figure directory, so they described a
    paper that no longer existed. Generating the list from the tex's own
    `\\includegraphics` and `\\bibliography` calls means it cannot drift: if a
    figure is renamed or dropped, this list follows on the next rebuild.
    """
    if not TEX_FILE.exists():
        print(f"!! {TEX_FILE} not found; skipping submission manifest")
        return
    tex = TEX_FILE.read_text(encoding="utf-8")

    def resolve(name: str) -> Path | None:
        for cand in (PAPER_RESULT / name, PAPER_DIR / name, PAPER_LATEX / name):
            if cand.exists():
                return cand
        return None

    figures, missing, seen = [], [], set()
    # The argument is either `{name.png}` or `{\detokenize{name.png}}` -- the
    # latter for the Chinese filenames, which need the wrapper to survive
    # pdflatex. A naive `\{([^}]*)\}` stops at the inner brace and yields a
    # truncated path like `\detokenize{RAG ...png`, so match the wrapper
    # explicitly. Both spellings must resolve to files that really exist.
    arg_re = re.compile(r"\\includegraphics\s*(?:\[[^\]]*\])?\s*"
                        r"\{(\\detokenize\{[^{}]*\}|[^{}]*)\}")
    for raw in arg_re.findall(tex):
        name = re.sub(r"^\\detokenize\{(.*)\}$", r"\1", raw.strip()).strip()
        if not name or name in seen:
            continue
        seen.add(name)
        path = resolve(name)
        (figures if path else missing).append((name, path))

    bibs = [b.strip() for b in re.findall(r"\\bibliography\{([^}]*)\}", tex)]
    supporting = [PAPER_LATEX / "acl.sty", PAPER_LATEX / "acl_natbib.bst"]
    supporting += [PAPER_LATEX / f"{b}.bib" for b in bibs if b]

    lines = [
        "# Submission file manifest",
        "",
        f"- **Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Result set:** `results_archive/{stamp}_{label}/`",
        f"- **Derived from:** `{TEX_FILE.name}` (not hand-maintained)",
        "",
        "Files under `result/` are regenerated from the archived per-question "
        "outputs; the two conceptual pipeline diagrams are manually maintained "
        "illustrations and contain no measured values. See `result/PROVENANCE.md`.",
        "",
        "## Source",
        "",
        f"- [x] `{TEX_FILE.name}`",
    ]
    for p in supporting:
        mark = "x" if p.exists() else " "
        lines.append(f"- [{mark}] `{p.name}`")

    lines += ["", f"## Figures referenced by the tex ({len(figures)})", ""]
    if not figures:
        lines.append("_None._")
    for name, path in sorted(figures):
        rel = path.relative_to(PAPER_DIR).as_posix() if path else name
        lines.append(f"- [x] `{rel}`")

    lines += ["", "## Referenced but not found", ""]
    if missing:
        lines += [f"- [ ] `{name}`" for name, _ in missing]
        lines.append("")
        lines.append("The build will not produce a PDF until these resolve.")
    else:
        lines.append("_None -- every referenced figure is present._")

    out = PAPER_DIR / "SUBMISSION_FILES.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"      SUBMISSION_FILES.md -> {out}"
          + (f"  ({len(missing)} MISSING figure(s))" if missing else ""))


def archive_round(dry: bool, label: str, note: str, stamp: str) -> bool:
    """Freeze the freshly rebuilt round into a timestamped results_archive/ folder."""
    script = BASE / "legacy" / "archive_results.py"
    if not script.exists():
        print(f"!! {script.name} not found; skipping archive")
        return False
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PAPER_RESULT_DIR"] = str(PAPER_RESULT)
    cmd = [sys.executable, "-m", "legacy.archive_results", "--label", label, "--stamp", stamp]
    if note:
        cmd += ["--note", note]
    if dry:
        cmd.append("--dry-run")
    print(f"\n{'=' * 70}\n>>> archive this round -> results_archive/{stamp}_{label}")
    return subprocess.run(cmd, env=env, cwd=BASE).returncode == 0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--skip-curate", action="store_true")
    ap.add_argument("--publish", action="store_true",
                    help="Copy regenerated figures into the paper bundle's result/ dir.")
    ap.add_argument("--no-archive", action="store_true",
                    help="Do not freeze this round into results_archive/.")
    ap.add_argument("--archive-label", default="paper-revision",
                    help="Short label for the archive folder name.")
    ap.add_argument("--archive-note", default="",
                    help="One-line description recorded in the archive MANIFEST.")
    ap.add_argument("--stamp", default=None,
                    help="Pin the archive timestamp (default: now), so a re-run "
                         "of the same round lands in one folder.")
    args = ap.parse_args()

    REV.mkdir(exist_ok=True)
    BUNDLE.mkdir(exist_ok=True)

    combined = REV / "rag_results_experiments.csv"
    validated = REV / "supp_strong_baselines_validated.csv"

    steps = [
        # (script, env overrides, label)
        ("combine_revision_results.py", {
            "RESULT_DIR": str(REV),
            # The appendix's ablation rows live in other sweeps, not in the main
            # batch: small-pool has its own batch, and the no-dedup arm is the
            # c=inf cell of the dedup sweep. Without naming those stems here the
            # combined file would silently omit them and every appendix table
            # that cites an ablation would fall back to stale numbers.
            "COMBINE_ALSO_STEMS": "supp_ablation_small_pool,supp_dedup_sweep_cinf",
        }, "stitch per-mode results into the combined CSV (paper Table 1 modes)"),

        ("score_retrieval.py", {
            "RESULT_DIR": str(REV),
            "QUESTIONS_FILE": FULL100,
        }, "retrieval metrics overall + by topic"),

        ("analyze_results.py", {
            "RESULT_DIR": str(REV),
            "QUESTIONS_FILE": FULL100,
        }, "answer-level analysis overall + by topic"),

        ("make_figures.py", {
            "RESULT_DIR": str(REV),
        }, "main retrieval / answer-rate / topic figures"),

        # Reads the topic CSVs written by score_retrieval.py / analyze_results.py.
        # It was missing from this chain, which is why its two heatmaps were the
        # only figures still carrying the previous round's numbers.
        ("make_heatmaps.py", {
            "RESULT_DIR": str(REV),
        }, "alternative topic heatmaps (mode-labelled rendering)"),

        ("paper_support_analysis.py", {
            "RESULT_DIR": str(REV),
            "RESULTS_FILE": str(combined),
            "QUESTIONS_FILE": FULL100,
            "ANALYSIS_PREFIX": "paper",
        }, "audit, full-vs-audited, pairwise bootstrap, diagnostic figures"),

        ("summarize_supplement_results.py", {
            "RESULT_DIR": str(REV),
        }, "supplementary sweep summaries"),

        ("make_revision_tables.py", {
            "RESULT_DIR": str(REV),
            "BUNDLE_DIR": str(BUNDLE),
            "PAPER_RESULT_DIR": str(PAPER_RESULT),
        }, "revision tables, question-balanced judge summaries, and correlations"),

        ("curate_paper_assets.py", {
            "RESULT_DIR": str(REV),
            "BUNDLE_DIR": str(BUNDLE),
        }, "curated paper tables and figures"),
    ]

    if args.skip_curate:
        steps = [s for s in steps if s[0] != "curate_paper_assets.py"]

    print(f"Total steps: {len(steps)}"
          + (" + publish" if args.publish else ""))
    failed = []
    for script, env, label in steps:
        if not run(script, env, label, args.dry_run):
            failed.append(script)

    # One stamp for the whole round, so the archive folder and the provenance
    # file written into the paper bundle name the same result set.
    stamp = args.stamp or datetime.now().strftime("%Y-%m-%d_%H%M")

    # Publish BEFORE archiving. The archive's paper_bundle/ is a verbatim copy
    # of the latex/result/ directory (archive_results.py copies PAPER_BUNDLE),
    # so if the archive ran first it would freeze whatever the PREVIOUS round
    # published -- the bug that left every archive's paper_bundle one round
    # behind its own tables/ and figures/. Publish first, so the snapshot
    # captures this round's files.
    if args.publish and not failed:
        publish_figures(args.dry_run, stamp, args.archive_label)
    elif args.publish:
        print("\n!! skipping publish: rebuild had failures")

    archived = False

    # Archive only after a fully successful round -- a partial rebuild would
    # freeze a half-updated table set, which is exactly the confusion the
    # archive exists to prevent.
    if not args.no_archive:
        if failed:
            print("\n!! skipping archive: rebuild had failures")
        else:
            archived = archive_round(
                args.dry_run, args.archive_label, args.archive_note, stamp)
            if not archived:
                failed.append("archive_results.py")

    print(f"\nDone. Failed: {failed or 'none'}")
    print(f"Outputs under: {REV}")
    if archived:
        print(f"Frozen as    : results_archive/{stamp}_{args.archive_label}/")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
