"""Figure-pair audit resolves the repository metadata without frozen downloads."""
import csv
import hashlib
import json

import pytest

from scripts import audit_figure_pairs as audit


def write_pair_repository(tmp_path, nested_source=False):
    root = tmp_path / "repository"
    source = root / "source_data" / audit.REL if nested_source else root / audit.REL
    source.parent.mkdir(parents=True)
    with source.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=[
            "split", "config_id", "qid", "group_id", "seed", "variant_id", "G_final", "U_sim"])
        writer.writeheader()
        for index in range(600):
            no_cap, post_cap = (1, 0) if index < 63 else (0, 1) if index < 80 else (1, 1)
            for config, utility in ((audit.OFF, no_cap), (audit.POST, post_cap)):
                writer.writerow({
                    "split": "test", "config_id": config, "qid": f"q{index:03d}",
                    "group_id": f"world{index // 2:03d}", "seed": index // 2,
                    "variant_id": index % 2, "G_final": 1, "U_sim": utility})
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    (root / "metadata").mkdir()
    (root / "metadata/MANIFEST.json").write_text(json.dumps({
        audit.REL.as_posix(): {"bytes": source.stat().st_size, "sha256": digest}}), encoding="utf-8")
    return root, source, digest


@pytest.mark.parametrize("nested_source", [False, True])
def test_figure_pairs_use_metadata_manifest_and_preserve_frozen_source_identity(
        tmp_path, monkeypatch, nested_source):
    root, source, digest = write_pair_repository(tmp_path, nested_source)
    output = tmp_path / "figure_audit"
    monkeypatch.setattr(audit, "ROOT", root)
    monkeypatch.setattr("sys.argv", ["audit_figure_pairs.py", "--output", str(output)])
    audit.main()
    report = json.loads((output / "F4_transition_check.json").read_text())
    assert report["status"] == "PASS"
    assert report["source"] == audit.REL.as_posix()
    assert report["source_bytes"] == source.stat().st_size
    assert report["source_sha256"] == digest
    assert report["task_pairs"] == 600 and report["independent_worlds"] == 300
    assert report["transitions"] == {"lost": 63, "gained": 17, "unchanged": 520}
    assert report["G_outcomes_identical_on_every_task"] is True
    with (output / "F4_task_pairs.csv").open(newline="") as stream:
        assert len(list(csv.DictReader(stream))) == 600
    assert not (root / "MANIFEST.json").exists()


def test_figure_pairs_reject_bytes_that_differ_from_metadata_manifest(tmp_path, monkeypatch):
    root, source, _ = write_pair_repository(tmp_path)
    source.write_bytes(source.read_bytes() + b"tampered\n")
    output = tmp_path / "figure_audit"
    monkeypatch.setattr(audit, "ROOT", root)
    monkeypatch.setattr("sys.argv", ["audit_figure_pairs.py", "--output", str(output)])
    with pytest.raises(ValueError, match="Frozen per-record bytes differ"):
        audit.main()
    assert not list(output.iterdir())
