"""Metric contract regression cases, including missing gold and repeated pages."""
import math
import unittest

from validation.audit_metrics import measure, split_urls, transition


class MetricAuditTests(unittest.TestCase):
    def test_missing_annotations_are_not_negative_labels(self):
        with self.assertRaises(ValueError):
            measure(["a"], ["a"], set())

    def test_unretrieved_gold_stays_in_idcg(self):
        result = measure(["a"], ["a"], {"a", "b"})
        self.assertAlmostEqual(result["url_ndcg_at_10_distinct_pages"], 1 / (1 + 1 / math.log2(3)))
        self.assertEqual(result["url_recall_at_10_distinct_pages"], .5)
        self.assertEqual(result["hit_at_10_chunk"], 1)

    def test_duplicate_gold_pages_do_not_inflate_ndcg(self):
        result = measure(["a", "a", "a"], ["a", "a"], {"a", "b"})
        self.assertLess(result["url_ndcg_at_10_distinct_pages"], 1)
        self.assertEqual(result["url_recall_at_10_distinct_pages"], .5)

    def test_duplicate_nongold_chunks_consume_only_chunk_ranks(self):
        result = measure(["x", "x", "a"], ["x", "x"], {"a"})
        self.assertEqual(result["first_gold_chunk_rank"], 3)
        self.assertEqual(result["first_gold_distinct_page_rank"], 2)
        self.assertEqual(result["first_gold_discount_at_10"], .5)
        self.assertAlmostEqual(result["url_ndcg_at_10_distinct_pages"], 1 / math.log2(3))

    def test_complete_ranking_mrr_is_not_mrr_at_10(self):
        result = measure(["x"] * 10 + ["a"], ["x"] * 4, {"a"})
        self.assertEqual(result["hit_at_10_chunk"], 0)
        self.assertEqual(result["first_gold_discount_at_10"], 0)
        self.assertAlmostEqual(result["mrr_first_gold_chunk"], 1 / 11)

    def test_final_hit_uses_delivered_evidence(self):
        result = measure(["a", "x"], ["x"], {"a"})
        self.assertEqual(result["hit_at_10_chunk"], 1)
        self.assertEqual(result["final_gold_page_hit"], 0)

    def test_empty_retrieval_is_zero_with_known_gold(self):
        result = measure([], [], {"a"})
        self.assertEqual(result["first_gold_discount_at_10"], 0)
        self.assertEqual(result["url_ndcg_at_10_distinct_pages"], 0)
        self.assertIsNone(result["first_gold_chunk_rank"])

    def test_url_matching_has_no_hidden_canonicalization(self):
        urls = split_urls(" https://example/a | https://example/b/ ")
        self.assertEqual(urls, ["https://example/a", "https://example/b/"])
        self.assertEqual(measure(urls, urls, {"https://example/a/"})["final_gold_page_hit"], 0)

    def test_cutoff_distinguishes_rank_degradation_from_final_loss(self):
        base, cand = {"first_gold_chunk_rank": 5}, {"first_gold_chunk_rank": 12}
        self.assertEqual(transition(base, cand, None), "worsened")
        self.assertEqual(transition(base, cand, 10), "lost")
        self.assertEqual(transition(base, cand, 4), "both_missing")

    def test_true_final_loss_has_base_within_cutoff(self):
        self.assertEqual(transition({"first_gold_chunk_rank": 1}, {"first_gold_chunk_rank": 5}, 4), "lost")

    def test_page_ndcg_is_one_for_all_gold_in_ideal_order(self):
        result = measure(["b", "a", "c", "x"], ["b", "a"], {"a", "b", "c"})
        self.assertEqual(result["url_ndcg_at_10_distinct_pages"], 1)
        self.assertEqual(result["url_recall_at_10_distinct_pages"], 1)


if __name__ == "__main__":
    unittest.main()
