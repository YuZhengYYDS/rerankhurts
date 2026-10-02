import json
from collections import Counter, defaultdict

CORPUS_FILE = "corpus_chunks.jsonl"


def main():
    rows = []
    with open(CORPUS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    print(f"Total chunks: {len(rows)}")

    by_url = Counter()
    by_title = Counter()
    lengths = []
    samples = defaultdict(list)

    for row in rows:
        url = row.get("url", "")
        title = row.get("title", "")
        text = row.get("text", "")

        by_url[url] += 1
        by_title[title] += 1
        lengths.append(len(text))

        if len(samples[url]) < 2:
            samples[url].append(text[:500])

    print("\nChunks per URL:")
    for url, cnt in by_url.most_common():
        print(f"{cnt:4d}  {url}")

    if lengths:
        print("\nLength stats:")
        print(f"min={min(lengths)}")
        print(f"max={max(lengths)}")
        print(f"avg={sum(lengths)/len(lengths):.1f}")

    print("\nSample chunks:")
    for url, chunk_list in samples.items():
        print("\n" + "=" * 100)
        print(url)
        for i, chunk in enumerate(chunk_list, 1):
            print(f"\n--- sample {i} ---")
            print(chunk)
            print()


if __name__ == "__main__":
    main()