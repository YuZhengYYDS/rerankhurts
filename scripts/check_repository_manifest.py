"""Verify or refresh the current source inventory, separately from frozen runs."""
import argparse
import json
from pathlib import Path

try:
    from .package_release import checked_file, collect_files, manifest_for
except ImportError:
    from package_release import checked_file, collect_files, manifest_for

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = "metadata/MANIFEST.json"


def inventory(root):
    root = Path(root).resolve()
    members = {name: path for name, path in collect_files(root).items() if name != MANIFEST}
    for archive in (root / "releases").rglob("*.zip"):
        checked_file(archive, root)
        members[archive.relative_to(root).as_posix()] = archive
    return manifest_for(members, root)


def refresh(root=ROOT):
    root = Path(root).resolve()
    records = inventory(root)
    path = root / MANIFEST
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes((json.dumps(records, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"))
    return records


def verify(root=ROOT):
    root = Path(root).resolve()
    recorded = json.loads((root / MANIFEST).read_bytes())
    if not isinstance(recorded, dict):
        raise ValueError("Repository manifest must be an object")
    actual = inventory(root)
    issues = [{"file": name, "kind": "missing"} for name in sorted(recorded.keys() - actual.keys())]
    issues += [{"file": name, "kind": "unlisted"} for name in sorted(actual.keys() - recorded.keys())]
    issues += [{"file": name, "kind": "identity mismatch"}
               for name in sorted(recorded.keys() & actual.keys()) if recorded[name] != actual[name]]
    return {"status": "FAIL" if issues else "PASS", "files": len(actual), "issues": issues}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--write", action="store_true", help="Refresh the current inventory before verification")
    args = parser.parse_args()
    if args.write:
        refresh(args.root)
    result = verify(args.root)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
