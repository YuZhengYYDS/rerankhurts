"""Download the exact public model snapshots used by the strengthening study."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from .backend import DEFAULT_MODELS, ROOT, model_identity
from .downstream import MODEL as ANSWER_MODEL, REVISION as ANSWER_REVISION
from .protocol import save_json


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--include-answer-model", action="store_true",
                        help="Also download the pinned local Qwen answer model")
    parser.add_argument("--verify-only", action="store_true", help="Hash already downloaded snapshots without network access")
    parser.add_argument("--output", type=Path, default=ROOT / "build/strengthening/model_snapshots.json")
    args = parser.parse_args(argv)
    specs = dict(DEFAULT_MODELS)
    if args.include_answer_model:
        specs["answer"] = {"model": ANSWER_MODEL, "sha": ANSWER_REVISION}
    if not args.verify_only:
        from huggingface_hub import model_info, snapshot_download
        for role, spec in specs.items():
            info = model_info(spec["model"], revision=spec["sha"], token=False)
            if info.sha != spec["sha"]:
                raise ValueError("Model revision did not resolve to the expected immutable SHA")
            files = [item.rfilename for item in info.siblings]
            weights = [] if role == "tokenizer" else [name for name in files if "/" not in name and name.endswith(".safetensors")]
            if role != "tokenizer" and not weights:
                weights = [name for name in files if "/" not in name and name.endswith(".bin")]
                if not weights:
                    raise ValueError(f"No compatible model weights: {spec['model']}")
            destination = ROOT / ".cache/models" / spec["model"].replace("/", "--") / spec["sha"]
            snapshot_download(repo_id=spec["model"], revision=spec["sha"], token=False,
                              local_dir=destination,
                              allow_patterns=["*.json", "*.txt", "*.model", "tokenizer*", "merges.txt"] + weights)
            print(json.dumps({"downloaded": spec["model"], "revision": spec["sha"]}), flush=True)
    recorded = {role: model_identity(spec) for role, spec in specs.items()}
    save_json(args.output, recorded)
    print(json.dumps({"status": "verified", "snapshots": len(recorded), "manifest": str(args.output)}))


if __name__ == "__main__":
    main()
