"""Read-only, standard-library integrity checks for the shipped frozen artifacts.

This checks local bytes against their recorded manifests. It does not authenticate
the manifests, rerun scientific scoring, download models, or require model caches.
Recorded Windows separators are interpreted identically on Windows and Linux.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import re

ROOT = Path(__file__).resolve().parents[1]
SIM_DATA = "experiments/simulation/data/pilot_v2"
SIM_RUN = "experiments/runs/simulation_pilot_v2"
SIM_RESULTS = "experiments/simulation/results/pilot_v2"
GENERATOR_CODE = {"generate.py": "experiments/simulation/generate.py",
                  "protocol.py": "experiments/protocol.py"}
E3_CODE = {"run_factorial.py": "experiments/run_factorial.py",
           "protocol.py": "experiments/protocol.py"}


def file_sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def identity_sha256(value):
    data = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def relative_path(root, base, recorded):
    """Reject absolute, traversal, drive-relative, ADS, and escaping link paths."""
    if not isinstance(recorded, str) or not recorded or "\x00" in recorded:
        raise ValueError("Expected a nonempty relative path")
    value = recorded.replace("\\", "/")
    parts = value.split("/")
    if (PurePosixPath(value).is_absolute() or PureWindowsPath(recorded).drive
            or any(p in {"", ".", ".."} or ":" in p for p in parts)):
        raise ValueError("Absolute paths, empty segments, traversal and drive/stream names are forbidden")
    project = Path(root).resolve()
    anchor = Path(base).resolve()
    target = anchor.joinpath(*parts).resolve()
    if not anchor.is_relative_to(project) or not target.is_relative_to(anchor):
        raise ValueError("Recorded path escapes its artifact directory")
    return target


class Checker:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.errors = []
        self.counts = Counter()
        self.section = ""

    def error(self, kind, path, detail):
        self.errors.append({"section": self.section, "kind": kind,
                            "path": str(path), "detail": str(detail)})

    def require(self, condition, detail):
        if not condition:
            raise ValueError(detail)

    def path(self, base, name):
        return relative_path(self.root, base, name)

    def read(self, name):
        path = self.path(self.root, name)
        with path.open(encoding="utf-8-sig") as handle:
            return json.load(handle)

    def verify(self, base, name, expected, size=None):
        self.counts[self.section] += 1
        try:
            path = self.path(base, name)
            self.require(isinstance(expected, str) and re.fullmatch(r"[0-9a-fA-F]{64}", expected),
                         "Expected a SHA-256 hex digest")
            if not path.is_file():
                self.error("missing_file", name, "Recorded file is absent or not a regular file")
                return
            actual = file_sha256(path)
            if actual != expected.lower():
                self.error("hash_mismatch", name, f"Expected {expected}; observed {actual}")
            if size is not None and (type(size) is not int or path.stat().st_size != size):
                self.error("size_mismatch", name, f"Expected {size}; observed {path.stat().st_size}")
        except (OSError, ValueError, TypeError) as exc:
            self.error("invalid_path_or_digest", name, exc)

    def mapping(self, base, values):
        self.require(isinstance(values, dict) and bool(values), "Empty or invalid hash mapping")
        for name, expected in values.items():
            self.verify(base, name, expected)

    def code_mapping(self, values, paths):
        self.require(isinstance(values, dict) and set(values) == set(paths),
                     "Code manifest has missing or unexpected entries")
        for name, path in paths.items():
            self.verify(self.root, path, values[name])

    def run_identity(self, folder, code_paths=None):
        manifest = self.read(folder + "/manifest.json")
        identity = manifest["identity"]
        self.require(identity_sha256(identity) == manifest["identity_hash"], "Run identity digest mismatch")
        for key in ("corpus", "questions"):
            self.verify(self.root, identity["settings"][key], identity[key + "_sha256"])
        if code_paths is None:
            self.mapping(self.root, identity["code_sha256"])
        else:
            self.code_mapping(identity["code_sha256"], code_paths)
        status = self.read(folder + "/status.json")
        self.require(status["status"] == "complete", "Run is not complete")
        self.require(status["observed_records"] == status["expected_records"] == manifest["expected_records"],
                     "Run record counts differ")
        return manifest

    def e0(self):
        entries = self.read("validation/results/input_manifest.json")
        self.require(isinstance(entries, list) and bool(entries), "Empty or invalid E0 input manifest")
        seen = set()
        for row in entries:
            name = row["path"]
            canonical = str(name).replace("\\", "/")
            self.require(canonical not in seen, "Duplicate E0 manifest path")
            seen.add(canonical)
            self.verify(self.root, name, row["sha256"], row["bytes"])

    def simulation_spec(self):
        spec = self.read(SIM_DATA + "/specification.json")
        self.require(spec["status"] == "complete" and spec["annotation_source"] == "synthetic_oracle",
                     "Incomplete or non-synthetic specification")
        self.require(set(spec["files"]) == {"corpus.jsonl", "questions.jsonl", "oracle.jsonl"},
                     "Simulation specification has missing or extra input files")
        for name, record in spec["files"].items():
            self.verify(self.root / SIM_DATA, name, record["sha256"])
        self.code_mapping(spec["code_sha256"], GENERATOR_CODE)

    def simulation_results(self):
        status = self.read(SIM_RESULTS + "/status.json")
        self.require(status["status"] == "complete" and status["observed_records"] == status["expected_records"],
                     "Simulation evaluation is incomplete")
        self.require(status["annotation_source"] == "synthetic_oracle" and status["valid_for_human_eval_claim"] is False,
                     "Unexpected simulation annotation scope")
        provenance = status["provenance"]
        self.require(set(provenance["input_files"]) == {"corpus.jsonl", "questions.jsonl", "oracle.jsonl", "specification.json"},
                     "Missing or extra simulation provenance input files")
        self.mapping(self.root / SIM_DATA, provenance["input_files"])
        self.verify(self.root / SIM_RUN, "manifest.json", provenance["run_manifest_sha256"])
        self.verify(self.root / SIM_RUN, "status.json", provenance["run_status_sha256"])
        manifest = self.run_identity(SIM_RUN)
        self.require(provenance["run_identity"] == manifest["identity_hash"], "Evaluation refers to a different run")
        self.require(status["expected_records"] == manifest["expected_records"], "Evaluation/run record count mismatch")
        self.require(provenance["model_snapshots"] == manifest["identity"]["models"], "Model provenance differs from run")
        self.require(provenance["inference_code_sha256"] == manifest["identity"]["code_sha256"], "Inference code provenance differs from run")
        self.mapping(self.root, provenance["inference_code_sha256"])
        self.code_mapping(provenance["generator_code_sha256"], GENERATOR_CODE)
        self.verify(self.root, "experiments/simulation/evaluate.py", provenance["evaluator_code_sha256"])
        spec = self.read(SIM_DATA + "/specification.json")
        self.require(provenance["generator_code_sha256"] == spec["code_sha256"], "Generator provenance differs from specification")
        required_outputs = {"per_record.csv", "summary.csv", "selection.json", "budget_feasibility.json"}
        self.require(set(status["output_sha256"]) == required_outputs, "Missing or extra evaluator output hashes")
        self.mapping(self.root / SIM_RESULTS, status["output_sha256"])
        for name in ("selection.json", "budget_feasibility.json"):
            payload = self.read(SIM_RESULTS + "/" + name)
            self.require(payload["provenance"] == provenance, f"Inconsistent embedded provenance: {name}")
        traces = provenance["trace_sha256"]
        self.mapping(self.root / SIM_RUN / "traces", traces)
        self.require(len(traces) == manifest["questions"] == status["tasks"], "Trace/question counts differ")
        # Include unexpected files: a stale trace must not silently escape the audit.
        trace_dir = self.path(self.root, SIM_RUN + "/traces")
        recorded = {str(self.path(trace_dir, name).relative_to(trace_dir)).replace("\\", "/") for name in traces}
        actual = {str(p.relative_to(trace_dir)).replace("\\", "/") for p in trace_dir.rglob("*.json.gz")}
        self.require(recorded == actual, "Trace inventory differs from recorded provenance")
        tokenizer = provenance["tokenizer_file_manifest"]
        model = tokenizer["model"]
        self.require(isinstance(model, str) and re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", model),
                     "Invalid tokenizer repository name")
        model_record = self.read(SIM_RUN + "/model_files/" + model.replace("/", "--") + ".json")
        self.require(model_record == tokenizer, "Tokenizer file manifest differs from recorded evaluation provenance")
        self.require(tokenizer["sha"] == manifest["identity"]["models"]["tokenizer"]["sha"], "Tokenizer revision differs")
        for name, expected in tokenizer["files"].items():
            self.path(self.root, name)
            self.require(isinstance(expected, str) and re.fullmatch(r"[0-9a-fA-F]{64}", expected), "Invalid tokenizer file digest")

    def finish(self):
        return {"status": "fail" if self.errors else "pass", "checked_file_references": sum(self.counts.values()),
                "checks_by_section": dict(self.counts), "errors": self.errors,
                "scope": "Local manifest consistency and recorded file bytes; not scientific rescoring or authentication of manifests.",
                "model_cache": "Not required or downloaded. The shipped tokenizer file manifest is checked for consistency; external model/tokenizer bytes are not checked."}


def check(root=ROOT):
    """Return a JSON-serializable integrity report without writing files."""
    checker = Checker(root)
    for section, action in (("e0", checker.e0), ("e3", lambda: checker.run_identity("experiments/runs/e3_m3", E3_CODE)),
                            ("simulation_spec", checker.simulation_spec), ("simulation_results", checker.simulation_results)):
        checker.section = section
        try:
            action()
        except (OSError, ValueError, TypeError, KeyError, AttributeError) as exc:
            checker.error("manifest_or_consistency_error", section, exc)
    return checker.finish()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT, help="Extracted repository root")
    args = parser.parse_args(argv)
    result = check(args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
