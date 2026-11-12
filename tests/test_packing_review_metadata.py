import hashlib
import json

import pytest

from experiments.supplements.packing_reanalysis_v1.analyze import completed_human_review


@pytest.fixture
def review_repository(tmp_path):
    folder = tmp_path / 'experiments/strengthening/data/strengthening_v1/audit/reviews'
    folder.mkdir(parents=True)
    records = []
    for label in ('A', 'B'):
        content = f'Completed review {label}\n'.encode()
        name = f'WORLD_REVIEW_RESULTS_{label}.md'
        (folder / name).write_bytes(content)
        records.append({'reviewer': label, 'file': name,
                        'sha256': hashlib.sha256(content).hexdigest()})
    path = folder / 'completion.json'
    path.write_bytes(json.dumps({'status': 'complete', 'worlds': list(range(60)),
                                'review_records': records}).encode())
    return tmp_path, path


def test_packing_metadata_links_the_completed_sample_review(review_repository):
    root, _ = review_repository
    result = completed_human_review(root)
    assert (result['status'], result['sampled_worlds'], result['rounds']) == ('complete', 60, 2)
    assert (root / result['completion_record']).is_file()


def test_unfinished_review_record_cannot_produce_completion_metadata(review_repository):
    root, path = review_repository
    record = json.loads(path.read_bytes())
    record['status'] = 'pending'
    path.write_bytes(json.dumps(record).encode())
    with pytest.raises(ValueError, match='complete 60-world'):
        completed_human_review(root)


def test_changed_review_text_cannot_reuse_completion_metadata(review_repository):
    root, path = review_repository
    (path.parent / 'WORLD_REVIEW_RESULTS_A.md').write_bytes(b'Replaced review\n')
    with pytest.raises(ValueError, match='checksum mismatch'):
        completed_human_review(root)
