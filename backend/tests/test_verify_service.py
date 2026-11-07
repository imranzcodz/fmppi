"""Tests for verify service stubs."""
from app.services.verify_service import global_verify, kinship_verify, local_verify


class TestLocalVerify:
    def test_returns_ranked_matches(self):
        result = local_verify(b"test image bytes")
        assert "query_hash" in result
        assert "matches" in result
        assert len(result["matches"]) == 2
        assert result["matches"][0]["score"] > result["matches"][1]["score"]

    def test_deterministic(self):
        r1 = local_verify(b"same bytes")
        r2 = local_verify(b"same bytes")
        assert r1 == r2

    def test_different_input_different_score(self):
        r1 = local_verify(b"image A")
        r2 = local_verify(b"image B")
        assert r1["query_hash"] != r2["query_hash"]


class TestGlobalVerify:
    def test_returns_web_match(self):
        result = global_verify(b"test image bytes")
        assert "query_hash" in result
        assert "matches" in result
        assert result["matches"][0]["source"] == "web-stub"


class TestKinshipVerify:
    def test_returns_score_and_confidence(self):
        result = kinship_verify(b"face a", b"face b")
        assert "score" in result
        assert "is_kin" in result
        assert "confidence" in result
        assert "model_version" in result
        assert 0.0 <= result["score"] <= 1.0
        assert 0.0 <= result["confidence"] <= 1.0

    def test_is_kin_threshold(self):
        # XOR of identical bytes gives 0 -> score 0 -> not kin
        result_same = kinship_verify(b"\xff" * 32, b"\xff" * 32)
        assert result_same["is_kin"] is False
        # Different bytes can produce score > 0.5 sometimes
        result_diff = kinship_verify(b"\xff" * 32, b"\x00" * 32)
        assert "is_kin" in result_diff
