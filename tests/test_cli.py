"""The dispatcher must preserve the recorded invocation and isolate reanalysis."""
from types import SimpleNamespace

import pytest

from rerankhuts import cli
from rerankhuts.paths import ROOT_FILE_RELOCATIONS


def test_e3_defaults_to_relocated_inputs_and_a_new_output_directory():
    args = cli.commands_for("e3", [])[0]
    assert args[args.index("--corpus") + 1] == ROOT_FILE_RELOCATIONS["corpus_chunks_v2.jsonl"]
    assert args[args.index("--questions") + 1] == ROOT_FILE_RELOCATIONS["questions_expanded_full_validated.jsonl"]
    assert args[args.index("--output") + 1] == "build/runs/e3"
    assert cli.E3_RUN not in args


def test_status_reads_relocated_metadata_without_a_root_alias(monkeypatch, tmp_path, capsys):
    metadata = tmp_path / "metadata"
    metadata.mkdir()
    (metadata / "release_status.json").write_text('{"status":"frozen"}\n')
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    assert cli.main(["status"]) == 0
    assert '"frozen"' in capsys.readouterr().out
    assert not (tmp_path / "release_status.json").exists()


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


def test_tables_uses_maintained_build_helpers():
    commands = cli.commands_for("tables", [])
    assert commands == [
        ["scripts/check_frozen_files.py"],
        ["scripts/paper/build_e3_table.py", cli.E3_RUN],
        ["scripts/paper/build_simulation_table.py", cli.SIM_RESULTS],
        ["scripts/paper/build_strengthening_table.py"],
    ]


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


@pytest.mark.parametrize("command,module", cli.LEGACY_MODULES.items())
def test_historical_commands_dispatch_to_package_modules(command, module):
    assert cli.commands_for(command, []) == [["-m", module]]
    with pytest.raises(ValueError, match="environment variables"):
        cli.commands_for(command, ["--output", "elsewhere"])


def test_historical_help_does_not_load_a_model(monkeypatch, capsys):
    def forbidden(*args, **kwargs):
        raise AssertionError("help must not execute a historical tool")
    monkeypatch.setattr(cli.subprocess, "run", forbidden)
    assert cli.main(["legacy-eval", "--help"]) == 0
    assert "environment variables" in capsys.readouterr().out


def test_staging_copies_inputs_without_touching_source(tmp_path):
    source = tmp_path / cli.E3_RUN
    source.mkdir(parents=True)
    for name in ("manifest.json", "status.json", "per_question.csv", "summary.csv"):
        (source / name).write_bytes(name.encode())
    cli.stage_e3_analysis(tmp_path)
    staged = tmp_path / "build/reanalysis/e3/per_question.csv"
    staged.write_bytes(b"recomputed")
    assert (source / "per_question.csv").read_bytes() == b"per_question.csv"
