"""Tests for rate limit module."""
from app.security.rate_limit import _window, check_rate_limit


class TestRateLimit:
    def test_allows_under_limit(self):
        assert check_rate_limit("user:1:/api/test", 100) is True
        assert check_rate_limit("user:1:/api/test", 100) is True

    def test_blocks_over_limit(self):
        key = "user:over:/api/test"
        for _ in range(5):
            assert check_rate_limit(key, 5) is True
        assert check_rate_limit(key, 5) is False

    def test_different_keys_independent(self):
        assert check_rate_limit("key-a", 1) is True
        assert check_rate_limit("key-b", 1) is True
        assert check_rate_limit("key-a", 1) is False

    def test_window_changes_over_time(self):
        import time

        w1 = _window()
        time.sleep(0.01)
        w2 = _window()
        assert w1 <= w2
