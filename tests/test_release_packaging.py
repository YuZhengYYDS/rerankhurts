"""Release safety and integrity checks use tiny temporary repositories only."""
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import zipfile

import pytest

from scripts import package_release as package
from scripts import verify_release as verify


@pytest.fixture
def repository(tmp_path):
    root = tmp_path / "repository"
    files = {
        "README.md": "Reproduction instructions\n",
        "LICENSE": "Example license\n",
        "pixi.toml": "[workspace]\n",
        "pixi.lock": "version: 6\n",
        ".env.example": "TOKEN=\n",
        "rerankhuts/__main__.py": "print('entrypoint')\n",
        "legacy/old.py": "print('archived source')\n",
        "legacy/migration_manifest.json": '{"old.py":"legacy/old.py"}\n',
        "release_status.json": '{"ready":false}\n',
        "docs/RESULTS_GUIDE.md": "Result directory guide\n",
        "docs/CODE_GUIDE.md": "Code directory guide\n",
        "scripts/tool.py": "print('tool')\n",
        "tests/test_tool.py": "def test_example(): pass\n",
        "data/input.jsonl": '{"input":1}\n',
        "questions_v2.jsonl": '{"qid":"one"}\n',
        "experiments/simulation/data/pilot_v2/oracle.jsonl": '{"private_to_scoring":true}\n',
        "paper/main.tex": "\\documentclass{article}\n",
        "paper/main.pdf": "%PDF-example\n",
        "paper/references.bib": "@misc{example}\n",
        "paper/main.bbl": "Bibliography needed for a standalone paper build\n",
        "results/final.csv": "qid,score\none,1\n",
        "result/old_result.json": '{"result":1}\n',
        "experiments/runs/frozen/traces/one.json.gz": "retained compressed trace\n",
        "experiments/simulation/results/pilot_v2/per_record.csv": "qid,U\none,1\n",
        "validation/report.json": '{"status":"PASS"}\n',
        "validation/audit.py": "print('audit')\n",
        "config/defaults.json": '{"seed":2027}\n',
    }
    excluded = [
        ".pixi/envs/default/python.exe", ".cache/model.bin", "environments/python.exe",
        "src/__pycache__/tool.pyc", "node_modules/dependency.js", ".pytest_cache/nodeids",
        "experiments/runs/frozen/cache/scores.json", "experiments/runs/smoke2/trace.json",
        "results_archive/old.csv", "github_release/old.py", "build/main.pdf",
        "oldrelease.zip", "nested/saved.ZIP", ".env", ".env.production", "credentials.json",
        "credentials/nested/token.txt", "secrets.yaml", "client_secret_123.json",
        "service_account.json", "private.pem", ".netrc", ".ssh/id_rsa",
        "paper/main.aux", "paper/main.log", "paper/unused.bbl", "paper/main.synctex.gz",
    ]
    for relative, content in {**files, **{name: "EXCLUDE-ME" for name in excluded}}.items():
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
    return root, files, excluded


def archive_manifest(path):
    with zipfile.ZipFile(path) as archive:
        name = next(name for name in archive.namelist() if name.endswith("/MANIFEST.json"))
        return json.loads(archive.read(name))


def test_release_membership_manifests_and_split_packages(repository):
    root, files, excluded = repository
    report = package.package(root, split=True)
    output = root / "dist"
    assert report["status"] == "PASS"
    assert set(report["archives"]) == set(verify.ARCHIVE_ROOTS)
    full = archive_manifest(output / "rerankhuts_icde2027.zip")
    assert set(full) == set(files)
    assert not set(full) & set(excluded)
    assert "MANIFEST.json" not in full
    assert json.loads((output / "manifest.json").read_bytes()) == full
    paper = archive_manifest(output / "paper_icde2027_clean.zip")
    assert set(paper) == {"main.tex", "main.pdf", "references.bib", "main.bbl"}
    code = archive_manifest(output / "rerankhuts_icde2027_code.zip")
    assert {"rerankhuts/__main__.py", "legacy/old.py", "validation/audit.py", "pixi.lock", "config/defaults.json"} <= set(code)
    assert {"release_status.json", "legacy/migration_manifest.json"} <= set(code)
    assert not any(name.startswith(("data/", "paper/", "results/")) for name in code)
    assert "questions_v2.jsonl" not in code
    assert "experiments/simulation/data/pilot_v2/oracle.jsonl" not in code
    results = archive_manifest(output / "rerankhuts_icde2027_results.zip")
    assert {"results/final.csv", "validation/report.json", "experiments/runs/frozen/traces/one.json.gz"} <= set(results)
    assert {"release_status.json", "docs/RESULTS_GUIDE.md", "docs/CODE_GUIDE.md"} <= set(results)
    assert "data/input.jsonl" not in results and "validation/audit.py" not in results
    for filename, expected_root in verify.ARCHIVE_ROOTS.items():
        with zipfile.ZipFile(output / filename) as archive:
            assert {name.split("/")[0] for name in archive.namelist()} == {expected_root}
            assert archive.namelist() == sorted(archive.namelist())
            assert {entry.date_time for entry in archive.infolist()} == {package.ZIP_TIMESTAMP}
    assert verify.verify_release(output) == report


def test_deterministic_archive_bytes_ignore_source_mtimes(repository):
    root, files, _ = repository
    package.package(root, split=True)
    before = {path.name: path.read_bytes() for path in (root / "dist").iterdir()}
    for name in files:
        os.utime(root / name, (1_700_000_000, 1_700_000_000))
    package.package(root, split=True)
    after = {path.name: path.read_bytes() for path in (root / "dist").iterdir()}
    assert before == after


def test_unsplit_rebuild_removes_only_managed_optional_archives(repository):
    root, _, _ = repository
    package.package(root, split=True)
    unrelated = root / "dist" / "other.txt"
    unrelated.write_text("keep", encoding="utf-8")
    package.package(root)
    assert unrelated.read_text(encoding="utf-8") == "keep"
    assert not (root / "dist" / "rerankhuts_icde2027_code.zip").exists()
    assert not (root / "dist" / "rerankhuts_icde2027_results.zip").exists()
    assert set(verify.verify_release(root / "dist")["archives"]) == verify.REQUIRED_ARCHIVES


def test_external_checksums_detect_tampering(repository):
    root, _, _ = repository
    package.package(root)
    path = root / "dist" / "rerankhuts_icde2027.zip"
    path.write_bytes(path.read_bytes() + b"unexpected appended payload")
    with pytest.raises(ValueError, match="Release checksum mismatch"):
        verify.verify_release(root / "dist")


def write_test_archive(path, payloads=None, manifest=None):
    payloads = payloads if payloads is not None else [("rerankhuts/file.txt", b"original")]
    manifest = manifest if manifest is not None else {
        "file.txt": {"bytes": 8, "sha256": hashlib.sha256(b"original").hexdigest()}}
    with zipfile.ZipFile(path, "w") as archive:
        for name, data in payloads:
            if isinstance(name, str):
                info = zipfile.ZipInfo(name)
                info.filename = name  # Keep crafted raw names even on Windows.
                name = info
            archive.writestr(name, data)
        raw = manifest if isinstance(manifest, bytes) else json.dumps(manifest).encode()
        archive.writestr("rerankhuts/MANIFEST.json", raw)


def test_embedded_manifest_detects_payload_tampering(tmp_path):
    path = tmp_path / "test.zip"
    write_test_archive(path, [("rerankhuts/file.txt", b"modified")])
    with pytest.raises(ValueError, match="Content hash mismatch"):
        verify.verify_archive(path)


@pytest.mark.parametrize("name", [
    "rerankhuts/../escape", "/rerankhuts/absolute", "C:/rerankhuts/file",
    "rerankhuts\\file", "rerankhuts/dir//file", "rerankhuts/dir/./file",
    "rerankhuts/file.", "rerankhuts/file ", "rerankhuts/NUL.txt", "rerankhuts/CON .txt",
    "rerankhuts/invalid?name", "rerankhuts/file:stream",
])
def test_rejects_unsafe_member_names(tmp_path, name):
    path = tmp_path / "unsafe.zip"
    write_test_archive(path, [(name, b"x")])
    with pytest.raises(ValueError, match="[Pp]ath"):
        verify.verify_archive(path)
    assert not (tmp_path / "escape").exists()


@pytest.mark.parametrize("names", [
    ["rerankhuts/file", "rerankhuts/file"],
    ["rerankhuts/file", "rerankhuts/FILE"],
    ["rerankhuts/caf\u00e9", "rerankhuts/cafe\u0301"],
    ["rerankhuts/file", "rerankhuts/file/child"],
])
def test_rejects_duplicate_or_aliased_members(tmp_path, names):
    path = tmp_path / "duplicate.zip"
    if names[0] == names[1]:
        with pytest.warns(UserWarning, match="Duplicate name"):
            write_test_archive(path, [(name, b"x") for name in names])
    else:
        write_test_archive(path, [(name, b"x") for name in names])
    with pytest.raises(ValueError, match="[Dd]uplicate|collision"):
        verify.verify_archive(path)


def test_rejects_symlink_zip_member(tmp_path):
    path = tmp_path / "symlink.zip"
    info = zipfile.ZipInfo("rerankhuts/file.txt")
    info.create_system = 3
    info.external_attr = (stat.S_IFLNK | 0o777) << 16
    write_test_archive(path, [(info, b"original")])
    with pytest.raises(ValueError, match="Non-regular archive member"):
        verify.verify_archive(path)


def test_rejects_source_symlink(repository, tmp_path):
    root, _, _ = repository
    secret = tmp_path / "outside.txt"
    secret.write_text("outside", encoding="utf-8")
    try:
        (root / "source.txt").symlink_to(secret)
    except OSError as error:
        pytest.skip(f"Creating symlinks is unavailable on this host: {error}")
    with pytest.raises(ValueError, match="Linked source file"):
        package.package(root)


@pytest.mark.parametrize("manifest,payloads,message", [
    ({}, [("rerankhuts/unlisted.txt", b"x")], "membership"),
    ({"missing.txt": {"bytes": 0, "sha256": hashlib.sha256(b"").hexdigest()}}, [], "membership"),
    ({"MANIFEST.json": {"bytes": 0, "sha256": hashlib.sha256(b"").hexdigest()}}, [], "include itself"),
    (b'{"x":{},"x":{}}', [], "Duplicate JSON key"),
])
def test_manifest_membership_and_schema_rejection(tmp_path, manifest, payloads, message):
    path = tmp_path / "test.zip"
    write_test_archive(path, payloads, manifest)
    with pytest.raises(ValueError, match=message):
        verify.verify_archive(path)


def test_rehashed_external_manifest_must_match_embedded(repository):
    root, _, _ = repository
    package.package(root)
    output = root / "dist"
    (output / "manifest.json").write_text("{}", encoding="utf-8")
    sums = json.loads((output / "sha256sums.json").read_bytes())
    sums["manifest.json"] = verify.file_sha256(output / "manifest.json")
    (output / "sha256sums.json").write_text(json.dumps(sums), encoding="utf-8")
    with pytest.raises(ValueError, match="External manifest differs"):
        verify.verify_release(output)


def test_changed_source_aborts_before_publishing(repository, monkeypatch):
    root, _, _ = repository
    original = package.manifest_for

    def snapshot_then_change(members, source_root):
        manifest = original(members, source_root)
        (root / "README.md").write_text("changed since snapshot", encoding="utf-8")
        return manifest

    monkeypatch.setattr(package, "manifest_for", snapshot_then_change)
    with pytest.raises(ValueError, match="Source changed during packaging"):
        package.package(root)
    assert not list((root / "dist").iterdir())


def test_standalone_verify_and_build_verify_clis(repository):
    root, _, _ = repository
    build = subprocess.run([sys.executable, str(Path(package.__file__)), "--root", str(root), "--split", "--verify"],
                           check=True, capture_output=True, text=True)
    assert json.loads(build.stdout)["status"] == "PASS"
    before = {p.name: p.stat().st_mtime_ns for p in (root / "dist").iterdir()}
    checked = subprocess.run([sys.executable, str(Path(verify.__file__)), str(root / "dist")],
                             check=True, capture_output=True, text=True)
    assert json.loads(checked.stdout)["status"] == "PASS"
    assert before == {p.name: p.stat().st_mtime_ns for p in (root / "dist").iterdir()}
