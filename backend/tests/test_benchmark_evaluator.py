"""Unit tests for offline recommendation ranking metrics."""
import pytest
from app.benchmarking.evaluator import (
    calculate_precision_at_k,
    calculate_recall_at_k,
    calculate_hit_rate_at_k,
    calculate_ndcg_at_k,
)


def test_ranking_metrics_hand_calculated():
    recommended = [101, 102, 103, 104, 105]
    relevant = {102, 105, 109}

    # At K=3: top 3 are [101, 102, 103]. Relevant hit is 102.
    assert calculate_precision_at_k(recommended, relevant, k=3) == pytest.approx(1 / 3)
    assert calculate_recall_at_k(recommended, relevant, k=3) == pytest.approx(1 / 3)
    assert calculate_hit_rate_at_k(recommended, relevant, k=3) == 1.0

    # At K=5: hits are 102 (idx 1) and 105 (idx 4).
    # Precision@5 = 2 / 5 = 0.4
    assert calculate_precision_at_k(recommended, relevant, k=5) == 0.4
    # Recall@5 = 2 / 3 = 0.6667
    assert calculate_recall_at_k(recommended, relevant, k=5) == pytest.approx(2 / 3)
    # HitRate@5 = 1.0
    assert calculate_hit_rate_at_k(recommended, relevant, k=5) == 1.0

    # NDCG@3:
    # item 102 is at rank 2 (index 1) -> dcg = 1 / log2(1 + 2) = 1 / log2(3) = 0.630929
    # ideal hits for K=3: min(|relevant|=3, k=3) = 3 items (at ranks 1, 2, and 3)
    # idcg = (1 / log2(2)) + (1 / log2(3)) + (1 / log2(4)) = 1.0 + 0.630929 + 0.5 = 2.130929
    # ndcg@3 = 0.630929 / 2.130929 = 0.29608
    ndcg3 = calculate_ndcg_at_k(recommended, relevant, k=3)
    assert ndcg3 == pytest.approx(0.29608, rel=1e-3)


def test_ranking_metrics_no_hits():
    recommended = [1, 2, 3]
    relevant = {10, 20}
    assert calculate_precision_at_k(recommended, relevant, k=3) == 0.0
    assert calculate_recall_at_k(recommended, relevant, k=3) == 0.0
    assert calculate_hit_rate_at_k(recommended, relevant, k=3) == 0.0
    assert calculate_ndcg_at_k(recommended, relevant, k=3) == 0.0
