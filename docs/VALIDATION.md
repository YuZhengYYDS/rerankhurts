# Tests and artifact verification

Run commands from the repository root. Python 3.11 and dependency versions are declared in `pixi.toml`.

```bash
pixi install --locked
pixi run --locked test
python scripts/check_repository_manifest.py
pixi run --locked verify
pixi run --locked strengthen-verify --require-complete
pixi run --locked stage-reanalysis --output build/validation/stage
pixi run --locked packing-reanalysis --output build/validation/packing
pixi run --locked oncology-coverage --output build/validation/oncology
python experiments/supplements/answers_2048_120_v1/verify.py
python scripts/check_world_review_records.py --output build/validation/world_reviews.json
```

Use a fresh output directory when repeating reanalysis. `test` executes the complete `tests/` suite. `verify` checks the frozen E0/E3/pilot identities and E3/pilot records. The other commands check the current source inventory, main experiment records and saved supplemental outcomes.

The tokenizer interval check uses the fixed local tokenizer snapshot:

```bash
pixi run --locked -e gpu python experiments/supplements/oncology_coverage_v1/verify_tokenizer_intervals.py --tokenizer .cache/models/google-bert--bert-base-uncased/86b5e0934494bd15c9632b12f734a8a67f723594
```

The GitHub Actions workflow runs the full suite and artifact checks on Windows and Linux. The original 2048-token execution module uses Linux `fcntl`; its tests execute on Linux. Symbolic-link tests execute where the host grants link creation. Tests against the actual tokenizer use the fixed snapshot downloaded during setup.

After changing delivered files, refresh and verify the current inventory:

```bash
python scripts/check_repository_manifest.py --write
python scripts/check_repository_manifest.py
```

Frozen-run identities are separate from the current inventory. The Oncology rubric records its original identities and the later metadata identity update. Its scorer verifies the current input identities and reproduces the saved coverage outcomes.

Build and independently verify release archives:

```bash
python scripts/package_release.py --split --verify
```

This creates full, code and results archives. When the input tree includes a manuscript, it also creates and verifies the corresponding manuscript archive.
