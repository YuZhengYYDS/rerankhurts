"""Integrity failures must be reported without altering the research artifact."""
import hashlib
import json
from pathlib import Path

import pytest

from scripts.check_frozen_files import E0_ARCHIVED_CODE, check, main, relative_path


def digest(value):
    return hashlib.sha256(value).hexdigest()


@pytest.fixture
def frozen_tree(tmp_path):
    def write(name, value):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode() if not isinstance(value, bytes) else value
        path.write_bytes(raw)
        return digest(raw)

    def hash_file(name):
        return digest((tmp_path / name).read_bytes())

    for name in ("legacy_input.csv", "corpus.jsonl", "questions.jsonl", "experiments/protocol.py",
                 "experiments/run_factorial.py", "experiments/simulation/generate.py",
                 "experiments/simulation/backend.py", "experiments/simulation/evaluate.py"):
        write(name, (name + "\n").encode())
    write("validation/results/input_manifest.json", [
        {"path": "legacy_input.csv", "bytes": (tmp_path / "legacy_input.csv").stat().st_size,
         "sha256": hash_file("legacy_input.csv")},
    ])
    data = "experiments/simulation/data/pilot_v2"
    run = "experiments/runs/simulation_pilot_v2"
    results = "experiments/simulation/results/pilot_v2"
    data_hashes = {name: write(data + "/" + name, b"{}\n") for name in ("corpus.jsonl", "questions.jsonl", "oracle.jsonl")}
    generator = {"generate.py": hash_file("experiments/simulation/generate.py"),
                 "protocol.py": hash_file("experiments/protocol.py")}
    write(data + "/specification.json", {"status": "complete", "annotation_source": "synthetic_oracle",
          "files": {k: {"sha256": v} for k, v in data_hashes.items()}, "code_sha256": generator})
    models = {"tokenizer": {"model": "example/tokenizer", "sha": "a" * 40}}
    for folder, synthetic in (("experiments/runs/e3_m3", False), (run, True)):
        identity = {
            "settings": {"corpus": data + "/corpus.jsonl" if synthetic else "corpus.jsonl",
                         "questions": data + "/questions.jsonl" if synthetic else "questions.jsonl"},
            "code_sha256": ({"experiments\\protocol.py": hash_file("experiments/protocol.py"),
                             "experiments\\simulation\\backend.py": hash_file("experiments/simulation/backend.py")}
                            if synthetic else {"protocol.py": hash_file("experiments/protocol.py"),
                                               "run_factorial.py": hash_file("experiments/run_factorial.py")}),
            "models": models,
        }
        for key in ("corpus", "questions"):
            identity[key + "_sha256"] = hash_file(identity["settings"][key])
        identity_hash = digest(json.dumps(identity, sort_keys=True, separators=(",", ":")).encode())
        manifest = {"identity": identity, "identity_hash": identity_hash, "expected_records": 20, "questions": 1}
        write(folder + "/manifest.json", manifest)
        write(folder + "/status.json", {"status": "complete", "observed_records": 20, "expected_records": 20})
    tokenizer = {"model": "example/tokenizer", "sha": "a" * 40,
                 "files": {"subdir\\tokenizer.json": digest(b"not shipped")}, "tokenizer_only": True}
    write(run + "/model_files/example--tokenizer.json", tokenizer)
    trace_hash = write(run + "/traces/example.json.gz", b"frozen opaque compressed bytes")
    manifest = json.loads((tmp_path / run / "manifest.json").read_text())
    provenance = {
        "input_files": {k: hash_file(data + "/" + k) for k in (*data_hashes, "specification.json")},
        "run_manifest_sha256": hash_file(run + "/manifest.json"), "run_status_sha256": hash_file(run + "/status.json"),
        "run_identity": manifest["identity_hash"], "model_snapshots": models,
        "inference_code_sha256": manifest["identity"]["code_sha256"], "generator_code_sha256": generator,
        "evaluator_code_sha256": hash_file("experiments/simulation/evaluate.py"),
        "tokenizer_file_manifest": tokenizer, "trace_sha256": {"example.json.gz": trace_hash},
    }
    outputs = {name: write(results + "/" + name, b"some,results\n") for name in ("per_record.csv", "summary.csv")}
    outputs.update({name: write(results + "/" + name, {"provenance": provenance})
                    for name in ("selection.json", "budget_feasibility.json")})
    write(results + "/status.json", {"status": "complete", "observed_records": 20, "expected_records": 20,
          "tasks": 1, "annotation_source": "synthetic_oracle", "valid_for_human_eval_claim": False,
          "provenance": provenance, "output_sha256": outputs})
    return tmp_path


def snapshot(root):
    return {str(p.relative_to(root)): p.read_bytes() for p in root.rglob("*") if p.is_file()}


def test_complete_artifact_is_read_only_and_does_not_require_models(frozen_tree, capsys):
    before = snapshot(frozen_tree)
    result = check(frozen_tree)
    assert result["status"] == "pass", result
    assert result["checked_file_references"] > 20
    assert main(["--root", str(frozen_tree)]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "pass"
    assert snapshot(frozen_tree) == before
    assert not (frozen_tree / ".cache").exists()


@pytest.mark.parametrize("name", [
    "legacy_input.csv", "experiments/run_factorial.py", "experiments/simulation/generate.py",
    "experiments/simulation/data/pilot_v2/oracle.jsonl", "experiments/simulation/evaluate.py",
    "experiments/simulation/results/pilot_v2/summary.csv", "experiments/runs/simulation_pilot_v2/traces/example.json.gz",
])
def test_tampered_frozen_file_fails(frozen_tree, name):
    path = frozen_tree / name
    path.write_bytes(path.read_bytes() + b"tampered")
    result = check(frozen_tree)
    assert result["status"] == "fail"
    assert any(e["kind"] == "hash_mismatch" for e in result["errors"]), result


@pytest.mark.parametrize("name", ["legacy_input.csv", "experiments/runs/e3_m3/manifest.json",
                                  "experiments/simulation/results/pilot_v2/summary.csv"])
def test_missing_file_fails(frozen_tree, name):
    (frozen_tree / name).unlink()
    result = check(frozen_tree)
    assert result["status"] == "fail"
    assert result["errors"]


@pytest.mark.parametrize("name", ["../outside", "..\\outside", "/absolute", "C:\\outside",
                                  "C:drive-relative", "\\\\server\\share", "file:stream", "a/../b", "a//b", ""])
def test_illegal_recorded_paths_rejected_before_read(tmp_path, name):
    with pytest.raises(ValueError):
        relative_path(tmp_path, tmp_path, name)


def test_windows_relative_paths_are_portable(tmp_path):
    assert relative_path(tmp_path, tmp_path, "a\\b\\file.json") == tmp_path / "a" / "b" / "file.json"


def test_bad_manifest_path_is_reported(frozen_tree):
    path = frozen_tree / "validation/results/input_manifest.json"
    entries = json.loads(path.read_text())
    entries[0]["path"] = "..\\outside.csv"
    path.write_text(json.dumps(entries))
    result = check(frozen_tree)
    assert result["status"] == "fail"
    assert any(e["kind"] == "invalid_path_or_digest" for e in result["errors"])


def test_e0_relocated_code_checks_archived_bytes_and_original_manifest(frozen_tree):
    manifest_path = frozen_tree / "validation/results/input_manifest.json"
    entries = json.loads(manifest_path.read_bytes())
    for original, relocated in E0_ARCHIVED_CODE.items():
        historical = ("original " + original).encode()
        archive = frozen_tree / relocated
        archive.parent.mkdir(parents=True, exist_ok=True)
        archive.write_bytes(historical)
        active = frozen_tree / "legacy" / original
        active.parent.mkdir(parents=True, exist_ok=True)
        active.write_bytes(b"maintained version with adapted imports and paths")
        entries.append({"path": original, "bytes": len(historical), "sha256": digest(historical)})
    manifest_path.write_text(json.dumps(entries))
    before = snapshot(frozen_tree)
    assert check(frozen_tree)["status"] == "pass"
    assert snapshot(frozen_tree) == before
    assert all(not (frozen_tree / name).exists() for name in E0_ARCHIVED_CODE)
    (frozen_tree / E0_ARCHIVED_CODE["run_rag_eval.py"]).write_bytes(b"tampered archive")
    report = check(frozen_tree)
    assert report["status"] == "fail"
    assert any(error["kind"] == "hash_mismatch" and "archive/code_20261022/run_rag_eval.py" in error["path"]
               for error in report["errors"])


def test_e0_missing_archive_does_not_fall_back_to_active_code(frozen_tree):
    name = "score_retrieval.py"
    historical = b"historical scorer"
    (frozen_tree / name).write_bytes(historical)
    manifest_path = frozen_tree / "validation/results/input_manifest.json"
    entries = json.loads(manifest_path.read_bytes())
    entries.append({"path": name, "bytes": len(historical), "sha256": digest(historical)})
    manifest_path.write_text(json.dumps(entries))
    report = check(frozen_tree)
    assert report["status"] == "fail"
    assert any(error["kind"] == "missing_file" and E0_ARCHIVED_CODE[name] in error["path"]
               for error in report["errors"])


def test_unrecorded_trace_fails(frozen_tree):
    (frozen_tree / "experiments/runs/simulation_pilot_v2/traces/extra.json.gz").write_bytes(b"extra")
    result = check(frozen_tree)
    assert result["status"] == "fail"
    assert any("inventory" in e["detail"] for e in result["errors"])


def test_malformed_manifest_returns_failure_json(frozen_tree, capsys):
    (frozen_tree / "validation/results/input_manifest.json").write_text("{")
    assert main(["--root", str(frozen_tree)]) == 1
    assert json.loads(capsys.readouterr().out)["status"] == "fail"
