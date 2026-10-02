"""The dispatcher must preserve the recorded invocation and isolate reanalysis."""
from types import SimpleNamespace

import pytest

from rerankhuts import cli


def test_e3_revisions_are_explicit_and_user_output_can_be_overridden():
    args = cli.commands_for("e3", ["--limit", "2", "--output", "experiments/runs/smoke_new"])[0]
    for flag, revision in zip(cli.E3_REVISIONS[::2], cli.E3_REVISIONS[1::2]):
        assert args[args.index(flag) + 1] == revision
        assert len(revision) == 40
    assert args[-2:] == ["--output", "experiments/runs/smoke_new"]


def test_verify_writes_only_to_build_and_never_runs_a_model():
    commands = cli.commands_for("verify", [])
    assert all("backend" not in " ".join(c) and "run_factorial" not in " ".join(c) for c in commands)
    for args in commands:
        if "--output" in args:
            assert args[args.index("--output") + 1].startswith("build/")


def test_subprocess_uses_current_interpreter_and_repo_cwd(monkeypatch, tmp_path):
    seen = []
    def run(args, **kwargs):
        seen.append((args, kwargs))
        return SimpleNamespace(returncode=0)
    monkeypatch.setattr(cli.subprocess, "run", run)
    assert cli.run_steps([["tool.py", "value with spaces"]], root=tmp_path) == 0
    assert seen == [([cli.sys.executable, "tool.py", "value with spaces"],
                     {"cwd": tmp_path, "check": False})]


def test_failure_stops_the_remaining_steps(monkeypatch):
    seen = []
    def run(args, **kwargs):
        seen.append(args)
        return SimpleNamespace(returncode=7)
    monkeypatch.setattr(cli.subprocess, "run", run)
    assert cli.run_steps([["first.py"], ["second.py"]]) == 7
    assert len(seen) == 1


def test_dry_run_has_no_execution_or_staging(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("dry-run must not mutate or execute")
    monkeypatch.setattr(cli.subprocess, "run", forbidden)
    monkeypatch.setattr(cli, "stage_e3_analysis", forbidden)
    assert cli.main(["--dry-run", "analyze-e3"]) == 0


def test_composite_rejects_ambiguous_forwarded_options():
    with pytest.raises(ValueError, match="no extra arguments"):
        cli.commands_for("verify", ["--output", "elsewhere"])


def test_staging_copies_inputs_without_touching_source(tmp_path):
    source = tmp_path / cli.E3_RUN
    source.mkdir(parents=True)
    for name in ("manifest.json", "status.json", "per_question.csv", "summary.csv"):
        (source / name).write_bytes(name.encode())
    cli.stage_e3_analysis(tmp_path)
    staged = tmp_path / "build/reanalysis/e3/per_question.csv"
    staged.write_bytes(b"recomputed")
    assert (source / "per_question.csv").read_bytes() == b"per_question.csv"
