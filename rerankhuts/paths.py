"""Repository locations and exact aliases for the relocated root data files.

Aliases translate recorded names only; they never select files by existence or
substitute different bytes. Integrity callers still verify the original digest.
"""
from __future__ import annotations

from pathlib import Path, PurePosixPath, PureWindowsPath

ROOT = Path(__file__).resolve().parents[1]
ONCOLOGY_DIR = ROOT / "data/oncology"
CORPUS_DIR = ONCOLOGY_DIR / "corpus"
QUESTIONS_DIR = ONCOLOGY_DIR / "questions"
REPORTS_DIR = ONCOLOGY_DIR / "reports"
SOURCES_DIR = ONCOLOGY_DIR / "sources"
METADATA_DIR = ROOT / "metadata"

ROOT_FILE_RELOCATIONS = {
    "corpus_chunks_v1.jsonl": "data/oncology/corpus/corpus_chunks_v1.jsonl",
    "corpus_chunks_v2.jsonl": "data/oncology/corpus/corpus_chunks_v2.jsonl",
    "questions.jsonl": "data/oncology/questions/questions.jsonl",
    "questions_expanded_full_prepurge.jsonl": "data/oncology/questions/questions_expanded_full_prepurge.jsonl",
    "questions_expanded_full_validated.jsonl": "data/oncology/questions/questions_expanded_full_validated.jsonl",
    "questions_judge_sample_validated.jsonl": "data/oncology/questions/questions_judge_sample_validated.jsonl",
    "corpus_expansion_report.csv": "data/oncology/reports/corpus_expansion_report.csv",
    "questions_expanded_leakfree_report.csv": "data/oncology/reports/questions_expanded_leakfree_report.csv",
    "data_sources.json": "data/oncology/sources/data_sources.json",
    "urls.txt": "data/oncology/sources/urls.txt",
    "MANIFEST.json": "metadata/MANIFEST.json",
    "release_status.json": "metadata/release_status.json",
}


def _relative_name(relative: str | Path) -> str:
    if not isinstance(relative, (str, Path)):
        raise ValueError("Expected a repository-relative path")
    value = str(relative).replace("\\", "/")
    if (not value or "\x00" in value or PurePosixPath(value).is_absolute()
            or PureWindowsPath(str(relative)).drive
            or any(part in {"", ".", ".."} or ":" in part for part in value.split("/"))):
        raise ValueError("Absolute paths, traversal, empty segments and drive/stream names are forbidden")
    return value


def resolve_repo_path(root: Path, relative: str | Path) -> Path:
    """Resolve a safe relative path, translating only the twelve old root names."""
    recorded = _relative_name(relative)
    relocated = ROOT_FILE_RELOCATIONS.get(recorded, recorded)
    project = Path(root).resolve()
    target = project.joinpath(*relocated.split("/")).resolve()
    if not target.is_relative_to(project):
        raise ValueError("Repository path escapes the repository through a link")
    return target


def oncology_path(name: str, *, root: Path = ROOT, group: str | None = None) -> Path:
    """Locate known oncology inputs or a new filename in an explicit data group."""
    filename = _relative_name(name)
    if "/" in filename:
        raise ValueError("Expected a single oncology filename")
    groups = {"corpus", "questions", "reports", "sources"}
    if group is not None:
        if group not in groups:
            raise ValueError(f"Unknown oncology data group: {group}")
        return resolve_repo_path(root, f"data/oncology/{group}/{filename}")
    known = ROOT_FILE_RELOCATIONS.get(filename)
    if known is not None and known.startswith("data/oncology/"):
        return resolve_repo_path(root, known)
    if filename.startswith("corpus") and filename.endswith(".jsonl"):
        group = "corpus"
    elif filename.startswith("questions") and filename.endswith(".jsonl"):
        group = "questions"
    elif filename.endswith(".csv"):
        group = "reports"
    else:
        raise ValueError(f"Unknown oncology filename; specify a data group: {name}")
    return resolve_repo_path(root, f"data/oncology/{group}/{filename}")
