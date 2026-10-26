"""Offline checks for maintained historical data paths and self-contained copies."""
import ast
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from legacy import archive_results
from legacy.paths import resolve_legacy_path
from rerankhuts.paths import ROOT_FILE_RELOCATIONS, oncology_path

ROOT = Path(__file__).resolve().parents[1]
DATA_FILES = {old: new for old, new in ROOT_FILE_RELOCATIONS.items() if new.startswith("data/oncology/")}


def script_parts(name, assignments=(), functions=(), root=ROOT):
    """Load path configuration/functions without importing GPU or API libraries."""
    path = ROOT / "legacy" / name
    tree = ast.parse(path.read_text(), filename=str(path))
    names = {"BASE", "BASE_DIR", "RESULT_DIR", *assignments}
    selected = [ast.ImportFrom(module="__future__", names=[ast.alias(name="annotations")], level=0)]
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in node.targets):
            selected.append(node)
        elif isinstance(node, ast.FunctionDef) and node.name in {*functions, "resolve_path"}:
            selected.append(node)
    namespace = {"__file__": str(root / "legacy" / name), "Path": Path, "os": os,
                 "json": json, "shutil": shutil, "oncology_path": oncology_path,
                 "resolve_legacy_path": resolve_legacy_path, "ROOT_FILE_RELOCATIONS": ROOT_FILE_RELOCATIONS}
    exec(compile(ast.fix_missing_locations(ast.Module(body=selected, type_ignores=[])), str(path), "exec"), namespace)
    return namespace


@pytest.mark.parametrize("old,new", ROOT_FILE_RELOCATIONS.items())
def test_legacy_known_aliases_are_exact(tmp_path, old, new):
    assert resolve_legacy_path(tmp_path, old) == tmp_path / new
    assert resolve_legacy_path(tmp_path, "./" + old) == tmp_path / new
    assert resolve_legacy_path(tmp_path, "custom/" + old) == tmp_path / "custom" / old
    absolute = tmp_path / "external" / old
    assert resolve_legacy_path(ROOT, absolute) == absolute


def test_explicit_custom_relative_override_remains_usable(tmp_path):
    assert resolve_legacy_path(tmp_path, "../other/input.jsonl") == tmp_path / "../other/input.jsonl"


@pytest.mark.parametrize("script,constant,name", [
    ("annotate_questions.py", "INPUT_FILE", "questions.jsonl"),
    ("annotate_questions.py", "OUTPUT_FILE", "questions_annotated.jsonl"),
    ("build_corpus.py", "SOURCES_FILE", "data_sources.json"),
    ("build_corpus.py", "OUTPUT_FILE", "corpus_chunks_v1.jsonl"),
    ("build_expanded_benchmark.py", "ORIGINAL_CORPUS", "corpus_chunks_v1.jsonl"),
    ("build_expanded_benchmark.py", "EXPANDED_CORPUS", "corpus_chunks_v2.jsonl"),
    ("build_expanded_benchmark.py", "ORIGINAL_QUESTIONS", "questions.jsonl"),
    ("build_expanded_benchmark.py", "EXPANDED_QUESTIONS", "questions_expanded.jsonl"),
    ("build_expanded_benchmark.py", "REVIEW_CHECKLIST", "questions_expanded_review.csv"),
    ("build_grounded_questions.py", "CORPUS", "corpus_chunks_v2.jsonl"),
    ("build_grounded_questions.py", "EXISTING", "questions_expanded.jsonl"),
    ("build_grounded_questions.py", "OUT_QUESTIONS", "questions_expanded_v2.jsonl"),
    ("purge_leaky_questions.py", "SOURCE", "questions_expanded_full_prepurge.jsonl"),
    ("purge_leaky_questions.py", "OUT", "questions_expanded_full_validated.jsonl"),
    ("purge_leaky_questions.py", "REPORT", "questions_expanded_leakfree_report.csv"),
    ("make_figures.py", "CORPUS_FILE", "corpus_chunks_v1.jsonl"),
    ("make_revision_tables.py", "EXPANDED_QUESTIONS", "questions_expanded_full_validated.jsonl"),
    ("run_p3_matrix.py", "FULL100", "questions.jsonl"),
    ("run_p4_expanded.py", "EXPANDED_CORPUS", "corpus_chunks_v2.jsonl"),
    ("run_p4_expanded.py", "EXPANDED_QUESTIONS", "questions_expanded_full_validated.jsonl"),
    ("build_revision_assets.py", "FULL100", "questions.jsonl"),
    ("run_rag_eval.py", "CORPUS_FILE", "corpus_chunks_v1.jsonl"),
    ("run_rag_eval.py", "QUESTIONS_FILE", "questions.jsonl"),
    ("score_retrieval.py", "QUESTIONS_FILE", "questions.jsonl"),
    ("analyze_results.py", "QUESTIONS_FILE", "questions.jsonl"),
    ("paper_support_analysis.py", "QUESTIONS_FILE", "questions.jsonl"),
])
def test_maintained_data_defaults_use_canonical_groups(monkeypatch, script, constant, name):
    monkeypatch.delenv(constant, raising=False)
    namespace = script_parts(script, [constant])
    assert Path(namespace[constant]) == oncology_path(name)


def test_source_config_url_alias_is_resolved_without_rewriting(tmp_path):
    source_dir = tmp_path / "data/oncology/sources"
    source_dir.mkdir(parents=True)
    (source_dir / "urls.txt").write_text("https://example.org/one\n\nhttps://example.org/two\n")
    source = {"type": "web_urls_file", "path": "urls.txt"}
    encoded = json.dumps(source).encode()
    config = source_dir / "data_sources.json"
    config.write_bytes(encoded)
    namespace = script_parts("build_corpus.py", functions=["iter_web_urls"], root=tmp_path)
    assert namespace["iter_web_urls"](json.loads(config.read_bytes())) == [
        "https://example.org/one", "https://example.org/two"]
    assert config.read_bytes() == encoded
    assert not (tmp_path / "urls.txt").exists()


def test_archive_collects_relocated_inputs_and_preserves_layout(tmp_path, monkeypatch):
    for relative in DATA_FILES.values():
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture\n")
    # An old source snapshot is provenance, not an additional live dataset.
    frozen = tmp_path / "archive/old/questions.jsonl"
    frozen.parent.mkdir(parents=True)
    frozen.write_text("old snapshot\n")
    monkeypatch.setattr(archive_results, "BASE_DIR", tmp_path)
    found = archive_results.collect_root_inputs()
    assert {p.relative_to(tmp_path).as_posix() for p in found} == set(DATA_FILES.values())
    destination = tmp_path / "snapshot/benchmark"
    copied = archive_results.copy_group(found, destination)
    assert {name for name, _ in copied} == set(DATA_FILES.values())
    for path in found:
        assert (destination / path.relative_to(tmp_path)).read_bytes() == path.read_bytes()


def test_archive_code_includes_helpers_and_excludes_old_source_snapshots(tmp_path, monkeypatch):
    expected = ["legacy/__init__.py", "legacy/paths.py", "legacy/build_corpus.py",
                "rerankhuts/__init__.py", "rerankhuts/paths.py"]
    for relative in [*expected, "legacy/archive/old.py"]:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# fixture\n")
    monkeypatch.setattr(archive_results, "BASE_DIR", tmp_path)
    found = {p.relative_to(tmp_path).as_posix() for p in archive_results.collect_code()}
    assert found == set(expected)


def test_historical_package_keeps_data_paths_and_importable_helpers(tmp_path):
    for relative in ["legacy/__init__.py", "legacy/paths.py", "legacy/generate_normalized_questions.py",
                     "rerankhuts/__init__.py", "rerankhuts/paths.py"]:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)
    for relative in DATA_FILES.values():
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text("fixture\n")
    namespace = script_parts("package_emnlp_results.py", ["COPY_PATHS", "COPY_PATTERNS"],
                             functions=["copy_result_assets"], root=tmp_path)
    expected = {tmp_path / value for value in DATA_FILES.values()}
    assert expected <= set(namespace["COPY_PATHS"])
    destination = tmp_path / "bundle"
    destination.mkdir()
    namespace["BUNDLE_DIR"] = destination
    namespace["copy_result_assets"]()
    for relative in DATA_FILES.values():
        assert (destination / relative).read_bytes() == (tmp_path / relative).read_bytes()
    check = subprocess.run([sys.executable, "-c",
        "from pathlib import Path; from legacy.paths import resolve_legacy_path; "
        "from legacy.generate_normalized_questions import rewrite_question; "
        "assert resolve_legacy_path(Path.cwd(), 'questions.jsonl').is_file(); "
        "assert 'non-small cell' in rewrite_question('Treatment for NSCLC?')[0]"],
        cwd=destination, env={**os.environ, "PYTHONPATH": ""}, text=True, capture_output=True)
    assert check.returncode == 0, check.stderr
