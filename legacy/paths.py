"""Path handling for maintained historical tools and explicit user overrides."""
from pathlib import Path

from rerankhuts.paths import ROOT_FILE_RELOCATIONS, resolve_repo_path


def resolve_legacy_path(root: Path, value: str | Path) -> Path:
    """Translate old root filenames while retaining custom override semantics.

    Environment variables and CLI arguments may name absolute files or custom
    relative locations. Only the exact relocated root filenames are aliases;
    a same-named file inside another directory remains that explicit file.
    """
    candidate = Path(value)
    if candidate.is_absolute():
        return candidate
    if candidate.as_posix() in ROOT_FILE_RELOCATIONS:
        return resolve_repo_path(root, candidate)
    return Path(root) / candidate
