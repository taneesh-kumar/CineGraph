# Recommendation System Offline Evaluation

This document outlines the offline recommendation evaluation framework used in CineGraph to evaluate recommendation utility without test data leakage.

## Evaluation Design

### 1. Per-User Time-Ordered Split
For each eligible user with sufficient rating interactions:
1. Ratings are retrieved ordered chronologically by timestamp (`rated_at ASC`).
2. The earlier 70% of ratings represent the user's **training profile**.
3. The remaining 30% of ratings represent the **held-out test set**.

### 2. Relevance Definition
A movie in the held-out test set is considered **relevant** if the user rated it $\ge 4.0$ on the 0.5–5.0 scale.

### 3. Evaluated Models
1. **Global Popularity Baseline**: Recommends the highest-volume rated movies across the dataset, excluding movies already present in the user's training history.
2. **CineGraph Collaborative Model**: Traverses the Neo4j graph using the user's training likes ($\ge 3.5$) to find peers with shared tastes and scores candidate movies by peer consensus.

### 4. Ranking Metrics Calculated
- **Precision@K**: $\frac{|\text{Recommended}_K \cap \text{Relevant}|}{K}$
- **Recall@K**: $\frac{|\text{Recommended}_K \cap \text{Relevant}|}{|\text{Relevant}|}$
- **NDCG@K**: Normalized Discounted Cumulative Gain accounting for position discount ($\frac{1}{\log_2(i+2)}$).
- **Hit Rate@K**: Proportion of users who received at least one relevant recommendation within their top-$K$ recommendations.
- **Catalog Coverage**: Percentage of the total 2,500-movie catalog that ever appears in generated top-$K$ recommendations.
