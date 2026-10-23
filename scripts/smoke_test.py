"""Automated live smoke test script for essential CineGraph API and system flows."""
import json
import sys
import urllib.request
from typing import Any, Dict, List, Tuple


def run_smoke_tests(base_url: str = "http://127.0.0.1:8000") -> bool:
    """
    Exercise essential API endpoints against the running CineGraph backend.
    Returns True if all tests pass, False if any critical check fails.
    """
    tests: List[Tuple[str, str, int, str]] = [
        ("Health Probe", f"{base_url}/health", 200, "status"),
        ("Readiness Probe", f"{base_url}/ready", 200, "status"),
        ("Dataset Summary", f"{base_url}/api/v1/analytics/summary", 200, "total_movies"),
        ("Top-Rated Movies", f"{base_url}/api/v1/analytics/top-rated?limit=3", 200, None),
        ("Genre Analytics", f"{base_url}/api/v1/analytics/genres", 200, None),
        ("Rating Distribution", f"{base_url}/api/v1/analytics/ratings/distribution", 200, None),
        ("Movie Detail (Tenet 217465)", f"{base_url}/api/v1/movies/217465", 200, "title"),
        ("Movie Rating Stats (Tenet 217465)", f"{base_url}/api/v1/analytics/movies/217465/ratings", 200, "rating_count"),
        ("Movie Search ('Soul')", f"{base_url}/api/v1/movies/search?q=Soul&limit=3", 200, None),
        ("Similar Movies (Tenet 217465)", f"{base_url}/api/v1/recommendations/movie/217465?limit=3", 200, "recommendations"),
        ("User Collaborative Recs (User 57304)", f"{base_url}/api/v1/recommendations/user/57304?limit=3", 200, "recommendations"),
        ("Sparse User Recs (User 9999999)", f"{base_url}/api/v1/recommendations/user/9999999?limit=3", 200, "recommendations"),
        ("Nonexistent Movie Detail (ID 9999999)", f"{base_url}/api/v1/movies/9999999", 404, "detail"),
    ]

    all_passed = True
    print(f"============================================================")
    print(f"CINEGRAPH SYSTEM SMOKE TEST SUITE — {base_url}")
    print(f"============================================================")

    for name, url, expected_status, expected_key in tests:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "CineGraph-SmokeTest/1.0"})
            with urllib.request.urlopen(req, timeout=10.0) as resp:
                status = resp.status
                body = json.loads(resp.read().decode())
                
                if status != expected_status:
                    print(f"FAILED: {name} - Expected HTTP {expected_status}, got {status}")
                    all_passed = False
                    continue

                if expected_key and expected_key not in body:
                    print(f"FAILED: {name} - Missing expected response key '{expected_key}'")
                    all_passed = False
                    continue

                preview = str(body)[:65].replace("\n", " ")
                print(f"PASS: {name} [{status}] -> {preview}...")

        except urllib.error.HTTPError as e:
            if e.code == expected_status:
                print(f"PASS: {name} [{e.code}] -> Correctly handled expected error.")
            else:
                print(f"FAILED: {name} - Unexpected HTTP error: {e.code} ({e.reason})")
                all_passed = False
        except Exception as e:
            print(f"FAILED: {name} - Connection or parsing error: {e}")
            all_passed = False

    print(f"============================================================")
    if all_passed:
        print("ALL SMOKE TESTS PASSED SUCCESSFULLY.")
    else:
        print("CRITICAL SMOKE TESTS FAILED.")
    print(f"============================================================")
    return all_passed


if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"
    success = run_smoke_tests(target_url)
    sys.exit(0 if success else 1)
