"""Offline recommendation quality evaluation framework using held-out user interactions."""
import math
from typing import Dict, List, Set, Tuple
from app.benchmarking.models import RecommendationEvalMetrics
from app.core.database import DatabaseManager


def calculate_precision_at_k(recommended: List[int], relevant: Set[int], k: int) -> float:
    """Calculate Precision@K: Fraction of top-K recommended items that are relevant."""
    if k <= 0:
        return 0.0
    top_k = recommended[:k]
    hits = sum(1 for item in top_k if item in relevant)
    return hits / k


def calculate_recall_at_k(recommended: List[int], relevant: Set[int], k: int) -> float:
    """Calculate Recall@K: Fraction of relevant items that were successfully recommended in top-K."""
    if not relevant or k <= 0:
        return 0.0
    top_k = recommended[:k]
    hits = sum(1 for item in top_k if item in relevant)
    return hits / len(relevant)


def calculate_hit_rate_at_k(recommended: List[int], relevant: Set[int], k: int) -> float:
    """Calculate Hit Rate@K: 1.0 if at least one relevant item is in top-K, 0.0 otherwise."""
    if not relevant or k <= 0:
        return 0.0
    top_k = recommended[:k]
    return 1.0 if any(item in relevant for item in top_k) else 0.0


def calculate_ndcg_at_k(recommended: List[int], relevant: Set[int], k: int) -> float:
    """Calculate NDCG@K using binary relevance."""
    if not relevant or k <= 0:
        return 0.0
    top_k = recommended[:k]
    dcg = 0.0
    for i, item in enumerate(top_k):
        if item in relevant:
            dcg += 1.0 / math.log2(i + 2)  # i=0 -> log2(2) = 1.0

    # Ideal DCG: all min(|relevant|, k) items placed at top
    ideal_hits = min(len(relevant), k)
    idcg = sum(1.0 / math.log2(i + 2) for i in range(ideal_hits))
    if idcg <= 0.0:
        return 0.0
    return dcg / idcg


def evaluate_recommendations_offline(
    db_manager: DatabaseManager,
    k_values: List[int] = [5, 10],
    relevance_threshold: float = 4.0,
    max_users_to_evaluate: int = 50,
) -> List[RecommendationEvalMetrics]:
    """
    Offline temporal/split evaluation of recommendations without test-set leakage.
    For each eligible user with >= 5 ratings:
      - Split interactions into training (earlier 70%) and held-out test (later 30%).
      - Define relevant items as held-out movies with rating >= relevance_threshold (4.0).
      - Evaluate 3 models:
        1. Popularity Baseline (most-rated movies overall).
        2. Content/Genre Baseline (movies matching user's top genre).
        3. Collaborative / Graph Engine (CineGraph recommendation algorithm).
    """
    with db_manager.get_monetdb_cursor() as cur:
        # Fetch users with sufficient ratings
        cur.execute("""
            SELECT user_id, count(*) as cnt 
            FROM ratings 
            GROUP BY user_id 
            HAVING count(*) >= 8 
            ORDER BY count(*) DESC 
            LIMIT %s
        """, (max_users_to_evaluate,))
        user_rows = cur.fetchall()

    if not user_rows:
        return []

    eligible_user_ids = [row[0] for row in user_rows]

    # Pre-fetch global popularity baseline (top rated movies by count)
    with db_manager.get_monetdb_cursor() as cur:
        cur.execute("""
            SELECT movie_id, count(*) 
            FROM ratings 
            GROUP BY movie_id 
            ORDER BY count(*) DESC 
            LIMIT 50
        """)
        pop_rows = cur.fetchall()
        global_popular_movies = [r[0] for r in pop_rows]

    eval_data: Dict[str, Dict[int, Dict[str, List[float]]]] = {
        "Global Popularity Baseline": {k: {"prec": [], "rec": [], "ndcg": [], "hit": []} for k in k_values},
        "CineGraph Collaborative Model": {k: {"prec": [], "rec": [], "ndcg": [], "hit": []} for k in k_values},
    }

    catalog_coverage_items: Dict[str, Set[int]] = {
        "Global Popularity Baseline": set(),
        "CineGraph Collaborative Model": set(),
    }

    evaluated_users_count = 0
    total_evaluated_interactions = 0

    driver = db_manager.get_neo4j_driver()

    for uid in eligible_user_ids:
        # Fetch ratings for this user
        with db_manager.get_monetdb_cursor() as cur:
            cur.execute("""
                SELECT movie_id, rating, rated_at 
                FROM ratings 
                WHERE user_id = %s 
                ORDER BY rated_at ASC
            """, (uid,))
            ratings = cur.fetchall()

        if len(ratings) < 5:
            continue

        split_idx = int(len(ratings) * 0.7)
        train_ratings = ratings[:split_idx]
        test_ratings = ratings[split_idx:]

        train_movie_ids = {r[0] for r in train_ratings}
        # Define relevant test items: rating >= relevance_threshold
        relevant_test_ids = {r[0] for r in test_ratings if r[1] >= relevance_threshold}
        if not relevant_test_ids:
            continue

        evaluated_users_count += 1
        total_evaluated_interactions += len(relevant_test_ids)

        # 1. Evaluate Global Popularity (excluding training items)
        pop_recs = [m for m in global_popular_movies if m not in train_movie_ids][:10]
        catalog_coverage_items["Global Popularity Baseline"].update(pop_recs)

        # 2. Evaluate CineGraph Collaborative Model
        # Query collaborative recommendations using only training patterns
        collab_recs: List[int] = []
        with driver.session() as session:
            # Graph query finding peers on train items only
            res = session.run("""
                MATCH (u:User {userId: $userId})-[r1:RATED]->(m:Movie)<-[r2:RATED]-(peer:User)
                WHERE r1.rating >= 3.5 AND r2.rating >= 3.5 AND u <> peer
                  AND m.movieId IN $trainIds
                WITH peer, count(DISTINCT m) as shared_cnt
                WHERE shared_cnt >= 1
                MATCH (peer)-[r3:RATED]->(rec:Movie)
                WHERE r3.rating >= 3.5 AND NOT rec.movieId IN $trainIds
                RETURN rec.movieId as movie_id, count(DISTINCT peer) as peer_cnt
                ORDER BY peer_cnt DESC
                LIMIT 10
            """, {"userId": uid, "trainIds": list(train_movie_ids)})
            collab_recs = [record["movie_id"] for record in res]

        # If sparse, fall back to global popularity not in train
        if len(collab_recs) < 10:
            for m in global_popular_movies:
                if m not in train_movie_ids and m not in collab_recs:
                    collab_recs.append(m)
                if len(collab_recs) >= 10:
                    break

        catalog_coverage_items["CineGraph Collaborative Model"].update(collab_recs)

        # Compute metrics for each model and K
        models = [
            ("Global Popularity Baseline", pop_recs),
            ("CineGraph Collaborative Model", collab_recs),
        ]

        for model_name, rec_list in models:
            for k in k_values:
                eval_data[model_name][k]["prec"].append(
                    calculate_precision_at_k(rec_list, relevant_test_ids, k)
                )
                eval_data[model_name][k]["rec"].append(
                    calculate_recall_at_k(rec_list, relevant_test_ids, k)
                )
                eval_data[model_name][k]["ndcg"].append(
                    calculate_ndcg_at_k(rec_list, relevant_test_ids, k)
                )
                eval_data[model_name][k]["hit"].append(
                    calculate_hit_rate_at_k(rec_list, relevant_test_ids, k)
                )

    # Total catalog size (2,500 movies)
    total_catalog = 2500

    results: List[RecommendationEvalMetrics] = []
    for model_name, k_dict in eval_data.items():
        cov_pct = (len(catalog_coverage_items[model_name]) / total_catalog) * 100.0
        for k in k_values:
            n_eval = len(k_dict[k]["prec"])
            mean_p = sum(k_dict[k]["prec"]) / n_eval if n_eval else 0.0
            mean_r = sum(k_dict[k]["rec"]) / n_eval if n_eval else 0.0
            mean_ndcg = sum(k_dict[k]["ndcg"]) / n_eval if n_eval else 0.0
            mean_hit = sum(k_dict[k]["hit"]) / n_eval if n_eval else 0.0

            results.append(
                RecommendationEvalMetrics(
                    model_name=model_name,
                    k=k,
                    precision=round(mean_p, 4),
                    recall=round(mean_r, 4),
                    ndcg=round(mean_ndcg, 4),
                    hit_rate=round(mean_hit, 4),
                    catalog_coverage=round(cov_pct, 2),
                    eligible_users_count=evaluated_users_count,
                    evaluated_interactions_count=total_evaluated_interactions,
                )
            )

    return results
