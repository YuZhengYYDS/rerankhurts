"""Tests for parsing selected emphasis in the current manuscript."""
import pytest

from scripts.check_manuscript import extract_paragraphs


def test_paragraphs_ignore_comments_and_preserve_nested_bold():
    text = (
        "% P: I-1\n"
        "% \\textbf{An old, commented-out opening.}\n"
        "An ordinary opening. Supporting text.\n"
        "% P: I-2\n"
        "% A note between the marker and the actual paragraph.\n"
        "\\textbf{A \\emph{nested} important finding.} More text.\n"
    )
    parsed = extract_paragraphs(text, "section.tex")
    assert [p["id"] for p in parsed] == ["I-1", "I-2"]
    assert [p["opening_bold"] for p in parsed] == [False, True]
    assert parsed[0]["opening"] == "An ordinary opening."
    assert parsed[1]["opening"] == r"A \emph{nested} important finding."


def test_missing_paragraph_opening_fails():
    with pytest.raises(RuntimeError, match="Missing paragraph opening"):
        extract_paragraphs("% P: I-1\n% Only a comment.\n", "section.tex")
