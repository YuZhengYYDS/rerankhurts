"""Strip this machine's directory layout out of the files we release.

Every per-question row records the question set and corpus it was run against,
and those columns used to be written as absolute paths:

    question_file = D:\\Pycharm\\DeepSeekLLM\\result\\...\\paper_questions_validated.jsonl

That is one machine's layout, not information about the experiment. It leaks the
author's filesystem into a released artifact, and worse, it makes two runs that
read the same file look like they read different ones -- the only part a reader
can compare is the tail, which is exactly the part that is the same.

`run_rag_eval.py` now writes these columns relative to the repository, so future
runs are clean. Results produced before that change still carry the absolute
form, and they are not worth re-running for a metadata fix, so the copies that
actually ship (the archive and the paper bundle) are normalized on the way out.

The rewrite is confined to path-shaped tokens: a token starting with the
repository root, ending at the next delimiter. Nothing else in the row is
touched, so no metric can change.
"""
from pathlib import Path
import re

BASE_DIR = Path(__file__).resolve().parents[1]

# A path beginning with the repository root, up to whatever delimiter follows:
# a comma, a quote, or end of line. Matches both separator styles because CSV
# writers are inconsistent about it.
_PATH_TOKEN = re.compile(
    re.escape(str(BASE_DIR)).replace(r"\\", r"[\\/]") + r"[^,\"\r\n]*"
)


def sanitize_text(text: str) -> str:
    """Rewrite repository-rooted absolute paths into relative posix paths."""
    def _rewrite(match: re.Match) -> str:
        raw = match.group(0)
        try:
            return Path(raw.replace("/", "\\")).relative_to(BASE_DIR).as_posix()
        except ValueError:
            # Not actually inside the repository (a sibling with a shared
            # prefix); leave it rather than mangle it.
            return raw

    return _PATH_TOKEN.sub(_rewrite, text)


def sanitize_file(path: Path, encoding: str = "utf-8-sig") -> bool:
    """Sanitize one file in place. Returns True if anything changed."""
    try:
        original = path.read_text(encoding=encoding)
    except (UnicodeDecodeError, OSError):
        return False
    cleaned = sanitize_text(original)
    if cleaned == original:
        return False
    path.write_text(cleaned, encoding=encoding)
    return True


if __name__ == "__main__":
    import sys

    targets = [Path(a).resolve() for a in sys.argv[1:]] or [BASE_DIR]
    changed = 0
    for target in targets:
        files = sorted(target.rglob("*.csv")) if target.is_dir() else [target]
        for f in files:
            if sanitize_file(f):
                changed += 1
                print(f"  sanitized: {f}")
    print(f"{changed} file(s) rewritten")
