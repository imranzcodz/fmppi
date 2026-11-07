"""G6 Performance Measurement Script.

Measures:
- API p95 response time (excluding inference) — target < 500ms
- Inference time per image — target < 2s

Usage:
    python scripts/measure_g6.py --base-url http://localhost:8000 --n 50
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
from pathlib import Path
from typing import List

import urllib.request


def percentile(sorted_vals: List[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    k = (len(sorted_vals) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_vals) - 1)
    if f == c:
        return sorted_vals[f]
    d0 = sorted_vals[f] * (c - k)
    d1 = sorted_vals[c] * (k - f)
    return d0 + d1


def measure_api(base_url: str, n: int = 50) -> dict:
    """Measure API endpoint response times (excluding inference)."""
    times: List[float] = []
    endpoint = f"{base_url.rstrip('/')}/health"

    for i in range(n):
        start = time.perf_counter()
        try:
            req = urllib.request.Request(endpoint)
            with urllib.request.urlopen(req, timeout=10) as resp:
                _ = resp.read()
        except Exception as exc:
            print(f"  Request {i+1}/{n} failed: {exc}")
            continue
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        print(f"  Request {i+1}/{n}: {elapsed*1000:.1f}ms")

    if not times:
        return {"error": "all requests failed"}

    times_sorted = sorted(times)
    return {
        "count": len(times),
        "mean_ms": round(statistics.mean(times) * 1000, 2),
        "p50_ms": round(percentile(times_sorted, 50) * 1000, 2),
        "p95_ms": round(percentile(times_sorted, 95) * 1000, 2),
        "p99_ms": round(percentile(times_sorted, 99) * 1000, 2),
        "max_ms": round(max(times) * 1000, 2),
        "min_ms": round(min(times) * 1000, 2),
        "p95_under_500ms": percentile(times_sorted, 95) * 1000 < 500,
    }


def measure_inference(base_url: str, n: int = 20, image_bytes: bytes = b"") -> dict:
    """Measure inference time per image via verify/local endpoint."""
    times: List[float] = []
    endpoint = f"{base_url.rstrip('/')}/verify/local"

    for i in range(n):
        start = time.perf_counter()
        try:
            import urllib.parse

            boundary = "----FMPPIBOUNDARY"
            body = (
                f"--{boundary}\r\n"
                f'Content-Disposition: form-data; name="file"; filename="face.jpg"\r\n'
                f"Content-Type: image/jpeg\r\n\r\n"
            ).encode() + image_bytes + f"\r\n--{boundary}--\r\n".encode()
            req = urllib.request.Request(
                endpoint,
                data=body,
                headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                _ = resp.read()
        except Exception as exc:
            print(f"  Inference {i+1}/{n} failed: {exc}")
            continue
        elapsed = time.perf_counter() - start
        times.append(elapsed)
        print(f"  Inference {i+1}/{n}: {elapsed*1000:.1f}ms")

    if not times:
        return {"error": "all inferences failed"}

    times_sorted = sorted(times)
    return {
        "count": len(times),
        "mean_ms": round(statistics.mean(times) * 1000, 2),
        "p50_ms": round(percentile(times_sorted, 50) * 1000, 2),
        "p95_ms": round(percentile(times_sorted, 95) * 1000, 2),
        "p99_ms": round(percentile(times_sorted, 99) * 1000, 2),
        "max_ms": round(max(times) * 1000, 2),
        "min_ms": round(min(times) * 1000, 2),
        "inference_under_2s": max(times) < 2.0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Measure FMPPI G6 performance gates")
    parser.add_argument("--base-url", required=True, help="Base URL of the deployed API")
    parser.add_argument("--n-api", type=int, default=50, help="Number of API requests")
    parser.add_argument("--n-inference", type=int, default=20, help="Number of inference requests")
    parser.add_argument("--output", default="g6_report.json", help="Output JSON report path")
    args = parser.parse_args()

    print(f"Measuring G6 performance against {args.base_url}")
    print("=" * 60)

    print("\n[API p95 response time]")
    api_result = measure_api(args.base_url, args.n_api)
    print(json.dumps(api_result, indent=2))

    print("\n[Inference time per image]")
    # Use a small valid JPEG header (not a real image, but tests the endpoint path)
    fake_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9"
    inf_result = measure_inference(args.base_url, args.n_inference, fake_jpeg)
    print(json.dumps(inf_result, indent=2))

    print("\n[G6 Gate Assessment]")
    api_pass = api_result.get("p95_under_500ms", False)
    inf_pass = inf_result.get("inference_under_2s", False)
    print(f"  API p95 < 500ms: {'PASS' if api_pass else 'FAIL'}")
    print(f"  Inference < 2s:  {'PASS' if inf_pass else 'FAIL'}")
    print(f"  G6 overall:      {'PASS' if api_pass and inf_pass else 'FAIL'}")

    report = {
        "base_url": args.base_url,
        "api": api_result,
        "inference": inf_result,
        "g6_pass": bool(api_pass and inf_pass),
        "measured_at": __import__("datetime").datetime.utcnow().isoformat() + "Z",
    }
    Path(args.output).write_text(json.dumps(report, indent=2))
    print(f"\nReport saved to {args.output}")


if __name__ == "__main__":
    main()
