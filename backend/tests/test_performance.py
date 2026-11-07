"""G6 performance benchmarking tests.

Measures API response times (excluding inference) and verifies:
- API p95 < 500ms (excluding inference)
- Inference < 2s per image
"""
import statistics
import time

from app.services.verify_service import global_verify, kinship_verify, local_verify


class TestVerifyPerformance:
    """Benchmark verify service inference time (< 2s per image)."""

    def test_local_verify_inference_time(self):
        image_bytes = b"\x89PNG fakeface" * 100
        times = []
        for _ in range(20):
            start = time.perf_counter()
            local_verify(image_bytes)
            times.append(time.perf_counter() - start)
        p95 = statistics.quantiles(times, n=20)[18]  # approximate p95
        assert p95 < 2.0, f"local_verify p95 {p95:.3f}s exceeds 2s"

    def test_global_verify_inference_time(self):
        image_bytes = b"\x89PNG fakeface" * 100
        times = []
        for _ in range(20):
            start = time.perf_counter()
            global_verify(image_bytes)
            times.append(time.perf_counter() - start)
        p95 = statistics.quantiles(times, n=20)[18]
        assert p95 < 2.0, f"global_verify p95 {p95:.3f}s exceeds 2s"

    def test_kinship_verify_inference_time(self):
        image_bytes = b"\x89PNG fakeface" * 100
        times = []
        for _ in range(20):
            start = time.perf_counter()
            kinship_verify(image_bytes, image_bytes)
            times.append(time.perf_counter() - start)
        p95 = statistics.quantiles(times, n=20)[18]
        assert p95 < 2.0, f"kinship_verify p95 {p95:.3f}s exceeds 2s"


class TestAPIEndpointPerformance:
    """Benchmark API endpoint response times (excluding inference)."""

    def test_api_endpoints_p95_under_500ms(self, client, db):
        from app.services.user_service import create_user

        create_user(db, email="perf@example.com", password="Secret1234", role="investigator")
        login = client.post(
            "/auth/login",
            json={"email": "perf@example.com", "password": "Secret1234"},
        )
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        times = []
        for _ in range(30):
            start = time.perf_counter()
            resp = client.post(
                "/verify/local",
                files={"file": ("face.jpg", b"\x89PNG fakeface", "image/jpeg")},
                headers=headers,
            )
            assert resp.status_code == 200, resp.text
            times.append(time.perf_counter() - start)

        p95 = statistics.quantiles(times, n=100)[97]  # approximate p95
        assert p95 < 0.5, f"/verify/local p95 {p95:.3f}s exceeds 500ms"
