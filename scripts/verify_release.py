"""Verify a release directory or a single archive without extracting it (stdlib only)."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import stat
import unicodedata
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE_ROOTS = {
    "rerankhuts_icde2027.zip": "rerankhuts",
    "paper_icde2027_clean.zip": "paper",
    "rerankhuts_icde2027_code.zip": "rerankhuts",
    "rerankhuts_icde2027_results.zip": "rerankhuts",
}
REQUIRED_ARCHIVES = {"rerankhuts_icde2027.zip", "paper_icde2027_clean.zip"}
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}\Z")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def safe_name(name):
    """Reject paths that can escape or alias files on Windows or POSIX."""
    require(isinstance(name, str) and bool(name), "Empty or non-string archive path")
    require(not any(c in name for c in '\\:<>"|?*') and not name.startswith("/"),
            f"Unsafe archive path: {name!r}")
    require(not any(ord(c) < 32 or ord(c) == 127 for c in name),
            f"Control character in archive path: {name!r}")
    reserved = {"con", "prn", "aux", "nul"} | {f"{p}{i}" for p in ("com", "lpt") for i in range(1, 10)}
    for part in name.split("/"):
        require(part not in {"", ".", ".."} and not part.endswith((".", " ")),
                f"Unsafe archive path: {name!r}")
        require(part.split(".", 1)[0].rstrip(" .").casefold() not in reserved,
                f"Reserved Windows path: {name!r}")
    return name


def collision_key(name):
    return unicodedata.normalize("NFC", name).casefold()


def unique_paths(names):
    keys = set()
    for name in names:
        safe_name(name)
        key = collision_key(name)
        require(key not in keys, f"Duplicate or aliased archive path: {name!r}")
        keys.add(key)
    for key in keys:
        parts = key.split("/")
        require(not any("/".join(parts[:i]) in keys for i in range(1, len(parts))),
                f"File/directory path collision: {key!r}")


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, f"Duplicate JSON key: {key!r}")
        result[key] = value
    return result


def read_json(payload):
    return json.loads(payload, object_pairs_hook=_unique_object)


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def validate_manifest(manifest):
    require(isinstance(manifest, dict), "Manifest must be a per-file object")
    unique_paths(manifest)
    for name, metadata in manifest.items():
        require(collision_key(name) != "manifest.json", "Manifest must not include itself")
        require(isinstance(metadata, dict) and set(metadata) == {"bytes", "sha256"},
                f"Invalid metadata for {name!r}")
        size = metadata["bytes"]
        require(isinstance(size, int) and not isinstance(size, bool) and size >= 0,
                f"Invalid byte count for {name!r}")
        require(isinstance(metadata["sha256"], str) and SHA256_PATTERN.fullmatch(metadata["sha256"]),
                f"Invalid SHA-256 for {name!r}")


def verify_archive(path, expected_root=None):
    path = Path(path)
    require(path.is_file() and not path.is_symlink(), f"Not a regular archive: {path}")
    with zipfile.ZipFile(path) as archive:
        entries = archive.infolist()
        require(bool(entries), "Empty archive")
        # ZipInfo normalizes backslashes on Windows and truncates NULs. Check
        # the stored name before relying on its normalized lookup key.
        unique_paths([entry.orig_filename for entry in entries])
        names = [entry.filename for entry in entries]
        unique_paths(names)
        roots = {name.split("/", 1)[0] for name in names}
        require(len(roots) == 1, "Archive must have exactly one top-level directory")
        root = next(iter(roots))
        require(root in {"rerankhuts", "paper"}, f"Unknown archive root: {root!r}")
        require(expected_root is None or root == expected_root, "Unexpected archive root")
        require(all("/" in name for name in names), "Files must reside below the archive root")
        for entry in entries:
            file_type = stat.S_IFMT((entry.external_attr >> 16) & 0xFFFF)
            require(not entry.is_dir() and file_type in {0, stat.S_IFREG},
                    f"Non-regular archive member: {entry.filename!r}")
            require(not entry.flag_bits & 1, "Encrypted archive members are unsupported")
        manifest_name = f"{root}/MANIFEST.json"
        require(manifest_name in names, "Missing embedded MANIFEST.json")
        require(archive.getinfo(manifest_name).file_size <= 16 * 1024 * 1024, "Oversized manifest")
        manifest = read_json(archive.read(manifest_name))
        validate_manifest(manifest)
        expected = {f"{root}/{name}" for name in manifest} | {manifest_name}
        require(set(names) == expected, "Archive membership differs from embedded manifest")
        total = 0
        for name, metadata in manifest.items():
            member = f"{root}/{name}"
            require(archive.getinfo(member).file_size == metadata["bytes"], f"Byte count mismatch: {name}")
            digest, size = hashlib.sha256(), 0
            with archive.open(member) as stream:
                for block in iter(lambda: stream.read(1024 * 1024), b""):
                    digest.update(block)
                    size += len(block)
            require(size == metadata["bytes"], f"Byte count mismatch: {name}")
            require(digest.hexdigest() == metadata["sha256"], f"Content hash mismatch: {name}")
            total += size
    return {"root": root, "files": len(manifest), "uncompressed_bytes": total,
            "sha256": file_sha256(path), "manifest": manifest}


def verify_release(directory):
    directory = Path(directory).resolve()
    sums_path = directory / "sha256sums.json"
    require(sums_path.is_file() and not sums_path.is_symlink(), "Missing regular sha256sums.json")
    sums = read_json(sums_path.read_bytes())
    require(isinstance(sums, dict), "Checksums must be an object")
    require((REQUIRED_ARCHIVES | {"manifest.json"}) <= set(sums), "Required release files missing from checksums")
    require(set(sums) <= (set(ARCHIVE_ROOTS) | {"manifest.json"}), "Unknown release checksum entries")
    optional = set(ARCHIVE_ROOTS) - REQUIRED_ARCHIVES
    require(not (set(sums) & optional) or optional <= set(sums), "Both split archives must be present")
    for name, digest in sums.items():
        safe_name(name)
        require(isinstance(digest, str) and SHA256_PATTERN.fullmatch(digest), f"Invalid checksum: {name}")
        path = directory / name
        require(path.is_file() and not path.is_symlink(), f"Missing regular release file: {name}")
        require(file_sha256(path) == digest, f"Release checksum mismatch: {name}")
    reports = {name: verify_archive(directory / name, ARCHIVE_ROOTS[name])
               for name in sorted(sums) if name in ARCHIVE_ROOTS}
    external = read_json((directory / "manifest.json").read_bytes())
    validate_manifest(external)
    require(external == reports["rerankhuts_icde2027.zip"]["manifest"],
            "External manifest differs from full archive manifest")
    return {"status": "PASS", "archives": {
        name: {key: value for key, value in report.items() if key != "manifest"}
        for name, report in reports.items()}, "checksummed_files": len(sums)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=ROOT / "dist",
                        help="Release directory (default: dist) or a single ZIP")
    args = parser.parse_args(argv)
    if args.path.is_dir():
        report = verify_release(args.path)
    else:
        report = verify_archive(args.path, ARCHIVE_ROOTS.get(args.path.name))
        report.pop("manifest")
        report["status"] = "PASS"
    print(json.dumps(report, indent=2, sort_keys=True))
    return report


if __name__ == "__main__":
    main()
