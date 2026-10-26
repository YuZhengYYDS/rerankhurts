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
        ".gitattributes": "*.jsonl text eol=lf\n",
        ".env.example": "TOKEN=\n",
        "rerankhuts/__main__.py": "print('entrypoint')\n",
        "legacy/old.py": "print('archived source')\n",
        "legacy/migration_manifest.json": '{"old.py":"legacy/old.py"}\n',
        "release_status.json": '{"ready":false}\n',
        "docs/RESULTS_GUIDE.md": "Result directory guide\n",
        "docs/CODE_GUIDE.md": "Code directory guide\n",
        "docs/STRENGTHENING_GUIDE.md": "Strengthening result interpretation guide\n",
        "scripts/tool.py": "print('tool')\n",
        "tests/test_tool.py": "def test_example(): pass\n",
        "data/input.jsonl": '{"input":1}\n',
        "questions_v2.jsonl": '{"qid":"one"}\n',
        "experiments/simulation/data/pilot_v2/oracle.jsonl": '{"private_to_scoring":true}\n',
        "experiments/README.md": "Experiment directory guide\n",
        "experiments/simulation/README.md": "Pilot experiment guide\n",
        "experiments/strengthening/README.md": "Strengthening design and reproduction guide\n",
        "experiments/strengthening/backend.py": "print('new inference backend')\n",
        "experiments/strengthening/study_plan.json": '{"status":"design_fixed_before_new_model_outcomes"}\n',
        "experiments/strengthening/data/strengthening_v1/corpus.jsonl": '{"text":"fictional evidence"}\n',
        "experiments/strengthening/data/strengthening_v1/specification.json": '{"schema_version":"strengthening-v1"}\n',
        "experiments/strengthening/data/strengthening_v1/audit/README.md": "Pending human review packet guide\n",
        "paper/main.tex": "\\documentclass{article}\n",
        "paper/main.pdf": "%PDF-example\n",
        "paper/references.bib": "@misc{example}\n",
        "paper/main.bbl": "Bibliography needed for a standalone paper build\n",
        "results/final.csv": "qid,score\none,1\n",
        "result/old_result.json": '{"result":1}\n',
        "experiments/runs/frozen/traces/one.json.gz": "retained compressed trace\n",
        "experiments/simulation/results/pilot_v2/per_record.csv": "qid,U\none,1\n",
        "experiments/runs/strengthening_v1/manifest.json": '{"expected_records":89280}\n',
        "experiments/runs/strengthening_v1/traces/one.json.gz": "new compressed trace\n",
        "experiments/strengthening/results/strengthening_v1/README.md": "New result file guide\n",
        "experiments/strengthening/results/strengthening_v1/per_record.csv": "qid,U_sim\none,1\n",
        "experiments/strengthening/results/strengthening_v1/integrity.json": '{"status":"PASS"}\n',
        "experiments/strengthening/results/strengthening_v1/primary_cap_order.png": "plot payload\n",
        "experiments/strengthening/results/strengthening_v1/answers/responses/one.json": '{"response":"unknown"}\n',
        "experiments/strengthening/results/strengthening_v1/timing/requests.jsonl": '{"latency_ms":1.0}\n',
        "validation/README.md": "Independent audit guide\n",
        "validation/report.json": '{"status":"PASS"}\n',
        "validation/audit.py": "print('audit')\n",
        "config/defaults.json": '{"seed":2027}\n',
    }
    excluded = [
        ".pixi/envs/default/python.exe", ".cache/model.bin", "environments/python.exe",
        "src/__pycache__/tool.pyc", "node_modules/dependency.js", ".pytest_cache/nodeids",
        "experiments/runs/frozen/cache/scores.json", "experiments/runs/smoke2/trace.json",
        "experiments/runs/strengthening_v1/cache/document_embeddings.npy",
        "experiments/strengthening/results/strengthening_v1/cache/temporary.json",
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


def test_strengthening_split_preserves_protocol_and_all_result_layers(repository):
    """Published split archives retain the new workflow without copying raw data."""
    root, files, excluded = repository
    package.package(root, split=True)
    output = root / "dist"
    full = archive_manifest(output / "rerankhuts_icde2027.zip")
    code = archive_manifest(output / "rerankhuts_icde2027_code.zip")
    results = archive_manifest(output / "rerankhuts_icde2027_results.zip")
    protocol_files = {".gitattributes", "experiments/strengthening/study_plan.json",
                      "experiments/strengthening/backend.py"}
    assert protocol_files <= set(code)
    result_files = {name for name in files if name.startswith((
        "experiments/runs/strengthening_v1/", "experiments/strengthening/results/"))}
    assert result_files <= set(results)
    assert not result_files & set(code)
    assert {"experiments/README.md", "experiments/strengthening/README.md",
            "experiments/simulation/README.md", "validation/README.md",
            "experiments/strengthening/study_plan.json", "docs/STRENGTHENING_GUIDE.md"} <= set(results)
    data_files = {name for name in files if name.startswith("experiments/strengthening/data/")}
    assert data_files <= set(full)
    assert not data_files & (set(code) | set(results))
    assert not set(excluded) & (set(code) | set(results) | set(full))
    # Every convenience-archive entry has the same content identity as the full release.
    for subset in (code, results):
        assert all(record == full[name] for name, record in subset.items())


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


def record_paper_build(root):
    """A tiny successful-build fixture; no TeX or actual PDF rendering needed."""
    paper = root / "paper"
    for name, content in {
        "figures/overview.pdf": b"figure PDF",
        "figures/main.pdf": b"another figure, not the compiled main.pdf",
        "local.sty": b"style source",
        "README.md": b"Build instructions can change independently",
        "build_table.py": b"# Not a TeX compilation input",
    }.items():
        path = paper / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)

    def identity(name):
        payload = (paper / name).read_bytes()
        return {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}

    record = {
        "status": "PASS",
        "inputs": {name: identity(name) for name in (
            "main.tex", "references.bib", "figures/overview.pdf", "figures/main.pdf", "local.sty")},
        "outputs": {name: identity(name) for name in ("main.pdf", "main.bbl")},
        "page_check": {"body_pages": 11, "total_pages": 12,
                       "exempt_material_starts_page": 12, "body_page_limit": 12},
    }
    (paper / "build_manifest.json").write_text(json.dumps(record), encoding="utf-8")
    return record


def test_successful_paper_build_is_bound_and_shipped(repository):
    root, _, _ = repository
    record_paper_build(root)
    # Documentation and table-generation Python are not compiler inputs.
    (root / "paper/README.md").write_text("Updated instructions", encoding="utf-8")
    assert package.package(root)["status"] == "PASS"
    paper = archive_manifest(root / "dist/paper_icde2027_clean.zip")
    assert {"build_manifest.json", "main.pdf", "main.bbl", "figures/main.pdf"} <= set(paper)


@pytest.mark.parametrize("body,exempt,total", [
    (12, 12, 12),  # Body and exempt material share the final physical page.
    (11, 11, 12),  # Exempt material can continue beyond a shared page.
    (12, 13, 13),  # Existing next-page layout remains valid at the body limit.
    (11, 12, 13),  # Existing layouts can have multiple exempt pages.
])
def test_paper_build_accepts_shared_or_next_page_exempt_material(repository, body, exempt, total):
    root, _, _ = repository
    record = record_paper_build(root)
    record["page_check"].update(body_pages=body, exempt_material_starts_page=exempt,
                                total_pages=total)
    (root / "paper/build_manifest.json").write_text(json.dumps(record), encoding="utf-8")
    assert package.package(root)["status"] == "PASS"
    shipped = archive_manifest(root / "dist/paper_icde2027_clean.zip")
    assert "build_manifest.json" in shipped


@pytest.mark.parametrize("exempt,total,message", [
    (11, 12, "exempt_material_starts_page"),
    (14, 14, "exempt_material_starts_page"),
    (True, 12, "exempt_material_starts_page"),
    (12.0, 12, "exempt_material_starts_page"),
    (12, 11, "total_pages"),
    (13, 12, "total_pages"),
    (12, True, "total_pages"),
    (12, 12.0, "total_pages"),
])
def test_paper_build_rejects_invalid_shared_page_boundaries(repository, exempt, total, message):
    root, _, _ = repository
    record = record_paper_build(root)
    record["page_check"].update(body_pages=12, exempt_material_starts_page=exempt,
                                total_pages=total)
    (root / "paper/build_manifest.json").write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        package.package(root)
    assert not (root / "dist").exists()


def test_paper_build_without_explicit_exempt_boundary_keeps_legacy_meaning(repository):
    root, _, _ = repository
    record = record_paper_build(root)
    del record["page_check"]["exempt_material_starts_page"]
    path = root / "paper/build_manifest.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    assert package.package(root)["status"] == "PASS"
    record["page_check"]["total_pages"] = record["page_check"]["body_pages"]
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match="total_pages"):
        package.package(root)


def test_paper_build_counts_body_float_after_endmatter_begins(repository):
    root, _, _ = repository
    record = record_paper_build(root)
    record["page_check"].update(body_pages=12, total_pages=12,
                                exempt_material_starts_page=11,
                                last_body_text_page=11, body_float_pages=[1, 12])
    path = root / "paper/build_manifest.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    assert package.package(root)["status"] == "PASS"
    record["page_check"]["body_float_pages"] = [1, 13]
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match="body_float_pages"):
        package.package(root)


@pytest.mark.parametrize("name", ["main.tex", "main.pdf", "main.bbl", "figures/overview.pdf"])
def test_stale_paper_input_or_output_blocks_packaging_before_copy(repository, name):
    root, _, _ = repository
    record_paper_build(root)
    path = root / "paper" / name
    original = path.read_bytes()
    path.write_bytes(bytes([original[0] ^ 1]) + original[1:])
    with pytest.raises(ValueError, match="Paper build SHA-256 mismatch"):
        package.package(root)
    assert not (root / "dist").exists()


@pytest.mark.parametrize("change", ["add", "remove"])
def test_paper_input_membership_changes_require_rebuild(repository, change):
    root, _, _ = repository
    record_paper_build(root)
    if change == "add":
        (root / "paper/figures/new.png").write_bytes(b"new compiler input")
    else:
        (root / "paper/references.bib").unlink()
    with pytest.raises(ValueError, match="Paper build input membership differs"):
        package.package(root)
    assert not (root / "dist").exists()


@pytest.mark.parametrize("name", ["../outside.tex", "C:/outside.tex", "figures\\outside.tex"])
def test_paper_build_manifest_rejects_escaping_input_names(repository, name):
    root, _, _ = repository
    record = record_paper_build(root)
    record["inputs"][name] = record["inputs"]["main.tex"]
    (root / "paper/build_manifest.json").write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match="[Pp]ath"):
        package.package(root)
    assert not (root / "dist").exists()


@pytest.mark.parametrize("field,value,message", [
    ("status", "FAILED", "status PASS"),
    ("body_pages", 13, "1 to 12 pages"),
    ("body_pages", True, "1 to 12 pages"),
    ("total_pages", 10, "total_pages"),
    ("exempt_material_starts_page", 10, "exempt_material_starts_page"),
])
def test_paper_build_rejects_failed_or_inconsistent_page_check(repository, field, value, message):
    root, _, _ = repository
    record = record_paper_build(root)
    if field == "status":
        record[field] = value
    else:
        record["page_check"][field] = value
    (root / "paper/build_manifest.json").write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        package.package(root)
    assert not (root / "dist").exists()


def test_paper_build_rejects_noncompiler_input_and_missing_output(repository):
    root, _, _ = repository
    record = record_paper_build(root)
    path = root / "paper/build_manifest.json"
    record["inputs"]["README.md"] = {"bytes": 0, "sha256": hashlib.sha256(b"").hexdigest()}
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match="invalid compiled input"):
        package.package(root)
    del record["inputs"]["README.md"]
    del record["outputs"]["main.bbl"]
    path.write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match="output membership differs"):
        package.package(root)
    assert not (root / "dist").exists()


def test_paper_change_between_build_check_and_archive_snapshot_is_rejected(repository, monkeypatch):
    root, _, _ = repository
    record_paper_build(root)
    original = package.manifest_for

    def change_then_snapshot(members, source_root):
        (root / "paper/main.tex").write_text("changed after build check", encoding="utf-8")
        return original(members, source_root)

    monkeypatch.setattr(package, "manifest_for", change_then_snapshot)
    with pytest.raises(ValueError, match="Paper build changed while preparing"):
        package.package(root)
    assert not (root / "dist").exists()


def record_current_paper_build(root):
    """Current source-only paper uses an external record and a PDF-only output."""
    record = record_paper_build(root)
    (root / "paper/build_manifest.json").unlink()
    (root / "paper/main.bbl").unlink()
    record.update(schema_version=2, paper_root="paper")
    del record["outputs"]["main.bbl"]
    (root / "validation/paper_build.json").write_text(json.dumps(record), encoding="utf-8")
    return record


def test_current_build_record_is_external_and_binds_clean_and_split_archives(repository):
    root, _, _ = repository
    record_current_paper_build(root)
    assert package.package(root, split=True)["status"] == "PASS"
    output = root / "dist"
    full = archive_manifest(output / "rerankhuts_icde2027.zip")
    paper = archive_manifest(output / "paper_icde2027_clean.zip")
    results = archive_manifest(output / "rerankhuts_icde2027_results.zip")
    assert "validation/paper_build.json" in full and "validation/paper_build.json" in results
    assert {"main.pdf", "figures/main.pdf"} <= set(paper)
    assert not {"main.bbl", "build_manifest.json", "paper_build.json"} & set(paper)
    assert verify.verify_release(output)["status"] == "PASS"


@pytest.mark.parametrize("name", ["main.tex", "main.pdf", "figures/overview.pdf"])
def test_current_external_build_rejects_stale_source_or_pdf(repository, name):
    root, _, _ = repository
    record_current_paper_build(root)
    path = root / "paper" / name
    payload = path.read_bytes()
    path.write_bytes(bytes([payload[0] ^ 1]) + payload[1:])
    with pytest.raises(ValueError, match="Paper build SHA-256 mismatch"):
        package.package(root)
    assert not (root / "dist").exists()


def test_current_external_build_rejects_stale_bibliography_scratch(repository):
    root, _, _ = repository
    record_current_paper_build(root)
    (root / "paper/main.bbl").write_text("stale scratch", encoding="utf-8")
    with pytest.raises(ValueError, match="scratch only"):
        package.package(root)


def test_competing_paper_build_records_fail_closed(repository):
    root, _, _ = repository
    record = record_current_paper_build(root)
    (root / "paper/build_manifest.json").write_text(json.dumps(record), encoding="utf-8")
    with pytest.raises(ValueError, match="Multiple paper build manifests"):
        package.package(root)


def rewrite_archive_with_updated_manifest(path, member, payload):
    """Simulate a fully rehashed archive whose recorded TeX build is stale."""
    with zipfile.ZipFile(path) as source:
        members = {name: source.read(name) for name in source.namelist()}
    manifest_name = next(name for name in members if name.endswith("/MANIFEST.json"))
    prefix = manifest_name.removesuffix("MANIFEST.json")
    manifest = json.loads(members[manifest_name])
    members[prefix + member] = payload
    manifest[member] = {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
    members[manifest_name] = json.dumps(manifest).encode()
    with zipfile.ZipFile(path, "w") as target:
        for name, data in members.items():
            target.writestr(name, data)


def test_standalone_archive_verifier_enforces_external_build_identity(repository):
    root, _, _ = repository
    record_current_paper_build(root)
    package.package(root)
    path = root / "dist/rerankhuts_icde2027.zip"
    rewrite_archive_with_updated_manifest(path, "paper/main.tex", b"changed TeX")
    with pytest.raises(ValueError, match="Paper build byte count mismatch"):
        verify.verify_archive(path)


def test_rehashed_clean_archive_must_match_full_release(repository):
    root, _, _ = repository
    package.package(root)
    output = root / "dist"
    path = output / "paper_icde2027_clean.zip"
    rewrite_archive_with_updated_manifest(path, "main.tex", b"different clean paper")
    sums = json.loads((output / "sha256sums.json").read_text())
    sums[path.name] = verify.file_sha256(path)
    (output / "sha256sums.json").write_text(json.dumps(sums))
    with pytest.raises(ValueError, match="Clean paper archive differs"):
        verify.verify_release(output)


def test_paper_builder_prefers_pdflatex_and_bibtex(monkeypatch):
    from scripts import build_paper
    monkeypatch.setattr(build_paper.shutil, "which", lambda name: "/tools/" + name)
    engine, commands = build_paper.compiler_commands()
    assert engine == "pdflatex"
    assert [Path(command[0]).name for command in commands] == ["pdflatex", "bibtex", "pdflatex", "pdflatex"]


def test_paper_builder_uses_explicit_tectonic_fallback(monkeypatch):
    from scripts import build_paper
    monkeypatch.setattr(build_paper.shutil, "which", lambda name: None)
    engine, commands = build_paper.compiler_commands(tectonic=Path("/tools/tectonic"))
    assert engine == "tectonic"
    assert commands == [["/tools/tectonic", "--keep-logs", "--keep-intermediates", "main.tex"]]
