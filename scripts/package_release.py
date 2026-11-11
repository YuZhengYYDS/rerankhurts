"""Build deterministic research releases, excluding local state and credentials."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat
import tempfile
import zipfile

try:
    from .verify_release import (ARCHIVE_ROOTS, file_sha256, read_json, require,
                                 safe_name, unique_paths, validate_manifest,
                                 verify_archive, verify_release, validate_paper_build,
                                 PAPER_BUILD_RECORD, PAPER_INPUT_SUFFIXES, PAPER_OUTPUT_NAMES, paper_input)
except ImportError:  # Direct invocation: python scripts/package_release.py
    from verify_release import (ARCHIVE_ROOTS, file_sha256, read_json, require,
                                safe_name, unique_paths, validate_manifest,
                                verify_archive, verify_release, validate_paper_build,
                                PAPER_BUILD_RECORD, PAPER_INPUT_SUFFIXES, PAPER_OUTPUT_NAMES, paper_input)

ROOT = Path(__file__).resolve().parents[1]
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)
EXCLUDED_DIRS = {
    ".git", ".pixi", ".cache", ".venv", "venv", "env", "environment", "environments",
    "__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache", ".tox", ".nox",
    "node_modules", "site-packages", "__pypackages__", "dist", "build", "cache",
    "results_archive", "github_release", ".ssh", ".aws", ".azure", ".kube", ".huggingface",
    "credentials", "secrets",
}
EXCLUDED_SUFFIXES = {
    ".pyc", ".pyo", ".aux", ".log", ".out", ".blg", ".bbl", ".fls", ".fdb_latexmk",
    ".toc", ".nav", ".snm", ".vrb", ".xdv", ".dvi", ".idx", ".ilg", ".ind",
    ".lof", ".lot", ".tmp", ".bak", ".swp", ".swo", ".zip", ".pem", ".key", ".p12", ".pfx",
}
SECRET_NAMES = {".netrc", "_netrc", ".npmrc", ".pypirc", ".git-credentials", "id_rsa",
                "id_ed25519", "token.json", "tokens.json", "access_token", "refresh_token"}
RESULT_SUPPORT_FILES = {
    "README.md", "guide.md", "LICENSE", "NOTICE", "metadata/release_status.json",
    "metadata/MANIFEST.json", "metadata/data_layout.json",
    "docs/RESULTS_GUIDE.md", "docs/CODE_GUIDE.md", "docs/STRENGTHENING_GUIDE.md", "experiments/README.md",
    "experiments/simulation/README.md", "experiments/strengthening/README.md",
    "experiments/strengthening/study_plan.json", "validation/README.md",
}


def excluded_directory(name):
    name = name.casefold()
    return name in EXCLUDED_DIRS or name.startswith("smoke")


def credential_name(name):
    name = name.casefold()
    return ((name.startswith(".env") and name != ".env.example") or name in SECRET_NAMES
            or name.startswith(("credentials", "secrets", "client_secret", "service_account"))
            or name.endswith((".credentials.json", ".credentials.yaml", ".credentials.yml")))


def included(path, root=ROOT):
    relative = path.relative_to(root)
    return (not any(excluded_directory(part) for part in relative.parts[:-1])
            and not path.name.casefold().startswith("smoke")
            and (path.suffix.casefold() not in EXCLUDED_SUFFIXES
                 or relative.as_posix().casefold() == "paper/main.bbl")
            and not path.name.casefold().endswith(".synctex.gz")
            and not credential_name(path.name))


def linked(path):
    metadata = path.lstat()
    return (stat.S_ISLNK(metadata.st_mode)
            or bool(getattr(metadata, "st_file_attributes", 0)
                    & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)))


def checked_file(path, root):
    require(not linked(path), f"Linked source file is not packageable: {path}")
    require(stat.S_ISREG(path.lstat().st_mode), f"Non-regular source file: {path}")
    require(path.resolve().is_relative_to(root), f"Source escapes repository: {path}")


def collect_files(root, output=None):
    root = Path(root).resolve(strict=True)
    output = Path(output).resolve() if output is not None else None
    paths = {}
    for directory, folders, files in os.walk(root, followlinks=False):
        retained = []
        for folder in sorted(folders):
            path = Path(directory) / folder
            if excluded_directory(folder) or path.resolve() == output:
                continue
            require(not linked(path), f"Linked source directory is not packageable: {path}")
            retained.append(folder)
        folders[:] = retained
        for filename in sorted(files):
            path = Path(directory) / filename
            if not included(path, root):
                continue
            checked_file(path, root)
            relative = path.relative_to(root).as_posix()
            safe_name(relative)
            # The repository inventory lives in metadata/MANIFEST.json. The
            # archive root is reserved for the inventory generated below.
            require(relative.casefold() != "manifest.json", "Root MANIFEST.json is reserved for the release")
            paths[relative] = path
    unique_paths(paths)
    return dict(sorted(paths.items()))


def is_result(relative):
    parts = relative.split("/")
    return (parts[:2] == ["experiments", "supplements"]
            or parts[0] in {"result", "results"} or parts[:2] == ["experiments", "runs"]
            or parts[:3] == ["experiments", "simulation", "results"]
            or parts[:3] == ["experiments", "strengthening", "results"]
            or (parts[0] == "validation" and Path(relative).suffix not in {".py", ".md", ".rst"}))


def is_code(relative):
    parts, path = relative.split("/"), Path(relative)
    if (parts[0] == "paper"
            or (is_result(relative) and parts[:2] != ["experiments", "supplements"])
            or any(p in {"data", "datasets", "inputs", "annotations"} for p in parts[:-1])):
        return False
    return (path.suffix.casefold() in {".py", ".sh", ".ps1", ".bat", ".cmd", ".toml", ".lock", ".yaml", ".yml", ".md", ".rst", ".ini", ".cfg"}
            or relative in {"metadata/release_status.json", "metadata/MANIFEST.json", "metadata/data_layout.json",
                            "legacy/migration_manifest.json", ".gitattributes",
                            "experiments/strengthening/study_plan.json"}
            or path.name.casefold() in {"license", "licence", "notice", ".gitignore", ".env.example", "data_sources.json"}
            or (path.name.startswith("requirements") and path.suffix == ".txt")
            or (path.suffix == ".json" and any(p in {"config", "configs"} for p in parts[:-1])))


def json_bytes(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def manifest_for(members, root):
    manifest = {}
    for relative, path in members.items():
        checked_file(path, root)
        manifest[relative] = {"bytes": path.stat().st_size, "sha256": file_sha256(path)}
    return manifest


def check_paper_build(root, paper):
    """Bind either build-record layout to the exact packaged source snapshot."""
    paper_root = root / "paper"
    candidates = [path for path in (root / PAPER_BUILD_RECORD, paper_root / "build_manifest.json")
                  if path.exists()]
    require(len(candidates) <= 1, "Multiple paper build manifests; remove the obsolete record")
    if not candidates:
        return {}
    path = candidates[0]
    checked_file(path, root)
    relative = path.relative_to(root).as_posix()
    legacy = path.parent == paper_root
    if legacy:
        require("build_manifest.json" in paper, "Paper build manifest is excluded from the release")
    else:
        require(included(path, root), "Paper build manifest is excluded from the release")
    payload = path.read_bytes()
    snapshot = {name: {"bytes": source.stat().st_size, "sha256": file_sha256(source)}
                for name, source in paper.items()}
    expected = validate_paper_build(read_json(payload), snapshot, legacy=legacy)
    identities = {f"paper/{name}": metadata for name, metadata in expected.items()}
    identities[relative] = {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
    return identities


def zip_info(name, size):
    info = zipfile.ZipInfo(name, date_time=ZIP_TIMESTAMP)
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | 0o644) << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    info.file_size = size
    return info


def write_archive(destination, root_name, members, manifest, source_root):
    unique_paths([*members, "MANIFEST.json"])
    manifest_payload = json_bytes(manifest)
    with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for relative in sorted([*members, "MANIFEST.json"]):
            member_name = f"{root_name}/{relative}"
            if relative == "MANIFEST.json":
                archive.writestr(zip_info(member_name, len(manifest_payload)), manifest_payload)
                continue
            path, expected = members[relative], manifest[relative]
            checked_file(path, source_root)
            digest, size = hashlib.sha256(), 0
            with path.open("rb") as source, archive.open(zip_info(member_name, expected["bytes"]), "w") as target:
                for block in iter(lambda: source.read(1024 * 1024), b""):
                    target.write(block)
                    digest.update(block)
                    size += len(block)
            require(size == expected["bytes"] and digest.hexdigest() == expected["sha256"],
                    f"Source changed during packaging: {path}")
    verify_archive(destination, root_name)


def package(root=ROOT, output=None, split=False):
    root = Path(root).resolve(strict=True)
    output = Path(output).resolve() if output is not None else root / "dist"
    require(output != root, "Output directory must differ from repository root")
    members = collect_files(root, output)
    require(bool(members), "No packageable source files")
    paper = {name.removeprefix("paper/"): path for name, path in members.items() if name.startswith("paper/")}
    paper_build = check_paper_build(root, paper) if paper else {}
    full_manifest = manifest_for(members, root)
    require(all(full_manifest.get(name) == metadata for name, metadata in paper_build.items()),
            "Paper build changed while preparing the release")
    selections = {"rerankhuts_icde2027.zip": members}
    if paper:
        selections["paper_icde2027_clean.zip"] = paper
    if split:
        selections["rerankhuts_icde2027_code.zip"] = {name: path for name, path in members.items() if is_code(name)}
        selections["rerankhuts_icde2027_results.zip"] = {
            name: path for name, path in members.items()
            if is_result(name) or name in RESULT_SUPPORT_FILES}
    output.mkdir(parents=True, exist_ok=True)
    # Publish only after all staged archives pass independent verification. A crash
    # during publication is detected by checksums, which are published last.
    with tempfile.TemporaryDirectory(prefix=".package-", dir=output) as temporary:
        staged = Path(temporary)
        for filename, selected in selections.items():
            selected_manifest = {
                name: full_manifest[f"paper/{name}" if filename == "paper_icde2027_clean.zip" else name]
                for name in selected}
            write_archive(staged / filename, ARCHIVE_ROOTS[filename], selected, selected_manifest, root)
        (staged / "manifest.json").write_bytes(json_bytes(full_manifest))
        checksums = {name: file_sha256(staged / name) for name in sorted([*selections, "manifest.json"])}
        (staged / "sha256sums.json").write_bytes(json_bytes(checksums))
        report = verify_release(staged)
        for name in [*sorted(selections), "manifest.json", "sha256sums.json"]:
            os.replace(staged / name, output / name)
    # Avoid leaving stale script-owned split archives in an unsplit release.
    for name in set(ARCHIVE_ROOTS) - set(selections):
        stale = output / name
        if stale.is_file() and not stale.is_symlink():
            stale.unlink()
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Repository root (default: this repository)")
    parser.add_argument("--output", type=Path, help="Output directory (default: ROOT/dist)")
    parser.add_argument("--split", action="store_true", help="Also write code-only and results-only convenience archives")
    parser.add_argument("--verify", action="store_true", help="Additionally verify the published release directory")
    args = parser.parse_args(argv)
    report = package(args.root, args.output, args.split)
    if args.verify:
        report = verify_release(args.output or args.root / "dist")
    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    main()
