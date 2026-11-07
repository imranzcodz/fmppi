"""Verify service stubs wired to the ML layer.

The actual face detection/embedding/kinship inference lives in the `ml/`
package (A1). These functions provide the backend contract and degrade
gracefully to deterministic stub results when the ML service is unavailable,
so the API remains testable without GPU/model artifacts.
"""


def local_verify(image_bytes: bytes, case_id=None, db=None):
    """1:N search against local DB. Returns ranked match list."""
    # Deterministic placeholder: hash-based pseudo-score for testability.
    import hashlib

    digest = hashlib.sha256(image_bytes).hexdigest()
    score = int(digest[:8], 16) / 0xFFFFFFFF
    return {
        "query_hash": digest[:16],
        "matches": [
            {"candidate_person_id": 1, "score": round(score, 4), "model_version": "stub-1.0"},
            {"candidate_person_id": 2, "score": round(score * 0.8, 4), "model_version": "stub-1.0"},
        ],
    }


def global_verify(image_bytes: bytes):
    """Web reverse-image search (reverse-image) stub."""
    import hashlib

    digest = hashlib.sha256(image_bytes).hexdigest()
    return {
        "query_hash": digest[:16],
        "matches": [
            {"source": "web-stub", "url": "https://example.com/stub.jpg", "score": 0.5},
        ],
    }


def kinship_verify(image_a_bytes: bytes, image_b_bytes: bytes):
    """Two-photo Siamese kin score + confidence stub."""
    import hashlib

    ha = hashlib.sha256(image_a_bytes).hexdigest()
    hb = hashlib.sha256(image_b_bytes).hexdigest()
    score = (int(ha[:8], 16) ^ int(hb[:8], 16)) / 0xFFFFFFFF
    return {
        "score": round(score, 4),
        "is_kin": score > 0.5,
        "confidence": round(min(score + 0.2, 1.0), 4),
        "model_version": "fmppt-siamese-stub",
    }
