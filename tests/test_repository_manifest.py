import pytest

from scripts.check_repository_manifest import refresh, verify


@pytest.fixture
def source(tmp_path):
    (tmp_path / "README.md").write_bytes(b"source\n")
    refresh(tmp_path)
    return tmp_path


def test_current_inventory_matches_exact_source_bytes(source):
    assert verify(source) == {"status": "PASS", "files": 1, "issues": []}


def test_source_inventory_includes_historical_release_archives(source):
    archive = source / "releases/20260928/code.zip"
    archive.parent.mkdir(parents=True)
    archive.write_bytes(b"archived release bytes")
    records = refresh(source)
    assert "releases/20260928/code.zip" in records
    assert verify(source) == {"status": "PASS", "files": 2, "issues": []}


@pytest.mark.parametrize("change,kind", [("modify", "identity mismatch"), ("remove", "missing"), ("add", "unlisted")])
def test_current_inventory_rejects_changed_missing_or_unlisted_source(source, change, kind):
    path = source / "README.md"
    if change == "modify":
        path.write_bytes(b"modified\n")
    elif change == "remove":
        path.unlink()
    else:
        (source / "extra.txt").write_bytes(b"new\n")
    result = verify(source)
    assert result["status"] == "FAIL"
    assert [issue["kind"] for issue in result["issues"]] == [kind]
