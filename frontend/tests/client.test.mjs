import { test, describe, beforeEach, afterEach } from "node:test";
import assert from "node:assert/strict";

// Mock environment and API base URL
process.env.NEXT_PUBLIC_API_URL = "http://127.0.0.1:8000";

describe("CineGraph Frontend API Client & Contracts", () => {
  let originalFetch;
  let lastFetchUrl = null;
  let lastFetchOptions = null;
  let mockResponse = { status: 200, ok: true, data: {} };

  beforeEach(() => {
    originalFetch = globalThis.fetch;
    globalThis.fetch = async (url, options) => {
      lastFetchUrl = url;
      lastFetchOptions = options;
      return {
        ok: mockResponse.ok,
        status: mockResponse.status,
        json: async () => mockResponse.data,
      };
    };
  });

  afterEach(() => {
    globalThis.fetch = originalFetch;
    lastFetchUrl = null;
    lastFetchOptions = null;
  });

  test("ApiError correctly initializes status, message, and payload", async () => {
    // Import client dynamically
    const { ApiError } = await import("../lib/api/client.ts");
    const err = new ApiError("Movie not found", 404, { detail: "MovieLens ID 99999 missing" });

    assert.equal(err.name, "ApiError");
    assert.equal(err.status, 404);
    assert.equal(err.message, "Movie not found");
    assert.deepEqual(err.data, { detail: "MovieLens ID 99999 missing" });
    assert.ok(err instanceof Error);
  });

  test("getHealth() requests /api/v1/health with Accept: application/json", async () => {
    const { apiClient } = await import("../lib/api/client.ts");
    mockResponse = {
      status: 200,
      ok: true,
      data: { status: "ok", service: "CineGraph API", version: "1.0.0" },
    };

    const res = await apiClient.getHealth();
    assert.equal(lastFetchUrl, "http://127.0.0.1:8000/api/v1/health");
    assert.equal(res.status, "ok");
    assert.equal(res.service, "CineGraph API");
  });

  test("getReadiness() requests /api/v1/ready and returns dual-engine status", async () => {
    const { apiClient } = await import("../lib/api/client.ts");
    mockResponse = {
      status: 200,
      ok: true,
      data: {
        status: "ready",
        neo4j: { status: "connected", details: null },
        monetdb: { status: "connected", details: null },
      },
    };

    const res = await apiClient.getReadiness();
    assert.equal(lastFetchUrl, "http://127.0.0.1:8000/api/v1/ready");
    assert.equal(res.status, "ready");
    assert.equal(res.neo4j.status, "connected");
    assert.equal(res.monetdb.status, "connected");
  });

  test("searchMovies() URL-encodes special characters and query strings", async () => {
    const { apiClient } = await import("../lib/api/client.ts");
    mockResponse = {
      status: 200,
      ok: true,
      data: [{ movie_id: 1, title: "Toy Story (1995)", genres: ["Adventure", "Animation"] }],
    };

    const res = await apiClient.searchMovies("Toy Story & Friends", 15);
    assert.equal(
      lastFetchUrl,
      "http://127.0.0.1:8000/api/v1/movies/search?q=Toy%20Story%20%26%20Friends&limit=15"
    );
    assert.equal(res.length, 1);
    assert.equal(res[0].movie_id, 1);
  });

  test("getMovieById() constructs correct REST entity path", async () => {
    const { apiClient } = await import("../lib/api/client.ts");
    mockResponse = {
      status: 200,
      ok: true,
      data: { movie_id: 2571, title: "Matrix, The (1999)", genres: ["Action", "Sci-Fi"] },
    };

    const res = await apiClient.getMovieById(2571);
    assert.equal(lastFetchUrl, "http://127.0.0.1:8000/api/v1/movies/2571");
    assert.equal(res.movie_id, 2571);
    assert.equal(res.title, "Matrix, The (1999)");
  });

  test("getMovieRecommendations() requests Neo4j similar movies endpoint", async () => {
    const { apiClient } = await import("../lib/api/client.ts");
    mockResponse = {
      status: 200,
      ok: true,
      data: {
        source_type: "movie",
        source_id: 1,
        source_title: "Toy Story (1995)",
        recommendations: [
          {
            movie_id: 3114,
            title: "Toy Story 2 (1999)",
            score: 0.85,
            genres: ["Adventure", "Animation"],
            explanation: "High shared genre and rating overlap",
          },
        ],
        total_found: 1,
      },
    };

    const res = await apiClient.getMovieRecommendations(1, 5);
    assert.equal(lastFetchUrl, "http://127.0.0.1:8000/api/v1/recommendations/movie/1?limit=5");
    assert.equal(res.source_type, "movie");
    assert.equal(res.recommendations.length, 1);
    assert.equal(res.recommendations[0].movie_id, 3114);
  });

  test("getUserRecommendations() requests Neo4j user collaborative endpoint", async () => {
    const { apiClient } = await import("../lib/api/client.ts");
    mockResponse = {
      status: 200,
      ok: true,
      data: {
        source_type: "user",
        source_id: 42,
        recommendations: [
          {
            movie_id: 296,
            title: "Pulp Fiction (1994)",
            score: 4.8,
            genres: ["Crime", "Drama"],
            explanation: "Users with similar tastes gave high ratings",
          },
        ],
        total_found: 1,
      },
    };

    const res = await apiClient.getUserRecommendations(42, 10);
    assert.equal(lastFetchUrl, "http://127.0.0.1:8000/api/v1/recommendations/user/42?limit=10");
    assert.equal(res.source_id, 42);
    assert.equal(res.recommendations[0].movie_id, 296);
  });

  test("getTopRatedMovies() formats MonetDB query bounds", async () => {
    const { apiClient } = await import("../lib/api/client.ts");
    mockResponse = {
      status: 200,
      ok: true,
      data: [
        {
          movie_id: 318,
          title: "Shawshank Redemption, The (1994)",
          avg_rating: 4.41,
          rating_count: 350,
          genres: ["Crime", "Drama"],
        },
      ],
    };

    const res = await apiClient.getTopRatedMovies(25, 10);
    assert.equal(
      lastFetchUrl,
      "http://127.0.0.1:8000/api/v1/analytics/top-rated?min_ratings=25&limit=10"
    );
    assert.equal(res[0].movie_id, 318);
    assert.equal(res[0].avg_rating, 4.41);
  });

  test("getRatingDistribution() retrieves 0.5-5.0 histogram counts", async () => {
    const { apiClient } = await import("../lib/api/client.ts");
    mockResponse = {
      status: 200,
      ok: true,
      data: [
        { rating: 4.0, count: 12500, percentage: 25.0 },
        { rating: 5.0, count: 7500, percentage: 15.0 },
      ],
    };

    const res = await apiClient.getRatingDistribution();
    assert.equal(lastFetchUrl, "http://127.0.0.1:8000/api/v1/analytics/ratings/distribution");
    assert.equal(res.length, 2);
    assert.equal(res[0].rating, 4.0);
  });

  test("HTTP 404 response throws ApiError with status and server error detail", async () => {
    const { apiClient, ApiError } = await import("../lib/api/client.ts");
    mockResponse = {
      status: 404,
      ok: false,
      data: { detail: "Movie with ID 999999 not found" },
    };

    await assert.rejects(
      async () => {
        await apiClient.getMovieById(999999);
      },
      (err) => {
        assert.ok(err instanceof ApiError);
        assert.equal(err.status, 404);
        assert.equal(err.message, "Movie with ID 999999 not found");
        return true;
      }
    );
  });

  test("Network connection drop raises ApiError with status 0", async () => {
    const { apiClient, ApiError } = await import("../lib/api/client.ts");
    globalThis.fetch = async () => {
      throw new TypeError("Failed to fetch");
    };

    await assert.rejects(
      async () => {
        await apiClient.getHealth();
      },
      (err) => {
        assert.ok(err instanceof ApiError);
        assert.equal(err.status, 0);
        assert.ok(err.message.includes("Failed to connect to CineGraph API"));
        return true;
      }
    );
  });
});
