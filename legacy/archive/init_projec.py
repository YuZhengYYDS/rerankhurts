from pathlib import Path

files = [
    ".env",
    "requirements.txt",
    "urls.txt",
    "questions.jsonl",
    "build_corpus.py",
    "run_rag_eval.py",
]

for file_name in files:
    path = Path(file_name)
    if not path.exists():
        path.touch()
        print(f"Created: {file_name}")
    else:
        print(f"Already exists: {file_name}")