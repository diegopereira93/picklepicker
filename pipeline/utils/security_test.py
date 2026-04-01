"""Tests for security utilities - sensitive data scrubbing."""

import logging
import pytest
from pipeline.utils.security import (
    scrub_sensitive_data,
    SensitiveDataFilter,
    mask_exception,
    SENSITIVE_PATTERNS,
)


class TestScrubSensitiveData:
    """Tests for scrub_sensitive_data function."""

    def test_scrubs_api_key_in_message(self):
        """API key patterns should be masked."""
        msg = "Error: api_key=sk-abc123def456"
        result = scrub_sensitive_data(msg)
        assert "sk-abc123def456" not in result
        assert "***" in result

    def test_scrubs_token_in_url(self):
        """Token in URL query parameters should be masked."""
        msg = "Request failed: https://api.example.com/data?token=secret123&other=value"
        result = scrub_sensitive_data(msg)
        assert "secret123" not in result
        assert "token=***" in result
        assert "other=value" in result  # Non-sensitive param preserved

    def test_scrubs_firecrawl_api_key(self):
        """Firecrawl API key pattern should be masked."""
        msg = "Failed with key=fc-test1234567890abcdef"
        result = scrub_sensitive_data(msg)
        assert "fc-test1234567890abcdef" not in result
        assert "***" in result

    def test_scrubs_bearer_token(self):
        """Bearer token in Authorization header should be masked."""
        msg = 'Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9'
        result = scrub_sensitive_data(msg)
        assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in result
        assert "***" in result

    def test_scrubs_password(self):
        """Password patterns should be masked."""
        msg = "Login failed for user with password=SuperSecret123!"
        result = scrub_sensitive_data(msg)
        assert "SuperSecret123!" not in result
        assert "***" in result

    def test_scrubs_database_url(self):
        """Database URL with embedded password should be masked."""
        msg = "postgresql://user:secretpass@localhost:5432/dbname"
        result = scrub_sensitive_data(msg)
        assert "secretpass" not in result
        assert ":***@" in result or "***" in result

    def test_handles_multiple_secrets(self):
        """Multiple secrets in one message should all be masked."""
        msg = "Error: api_key=key1 and token=token2 and secret=mysecret"
        result = scrub_sensitive_data(msg)
        assert "key1" not in result
        assert "token2" not in result
        assert "mysecret" not in result

    def test_preserves_non_sensitive_text(self):
        """Non-sensitive text should be preserved."""
        msg = "This is a normal error message without secrets"
        result = scrub_sensitive_data(msg)
        assert result == msg

    def test_custom_replacement(self):
        """Custom replacement string should be used."""
        msg = "api_key=secret123"
        result = scrub_sensitive_data(msg, replacement="[REDACTED]")
        assert "[REDACTED]" in result

    def test_handles_empty_string(self):
        """Empty string should return empty."""
        assert scrub_sensitive_data("") == ""

    def test_handles_none_gracefully(self):
        """None input should return empty string."""
        assert scrub_sensitive_data(None) == ""


class TestSensitiveDataFilter:
    """Tests for SensitiveDataFilter logging filter."""

    def test_filter_scrubs_log_message(self):
        """Filter should scrub sensitive data from log messages."""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Error with api_key=secret123",
            args=(),
            exc_info=None,
        )
        filter_obj.filter(record)
        assert "secret123" not in record.msg
        assert "***" in record.msg

    def test_filter_scrubs_log_args(self):
        """Filter should scrub sensitive data from log args."""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Error with %s",
            args=("api_key=secret123",),
            exc_info=None,
        )
        filter_obj.filter(record)
        assert "secret123" not in record.args[0]

    def test_filter_handles_non_string_args(self):
        """Filter should handle non-string args gracefully."""
        filter_obj = SensitiveDataFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Count: %d",
            args=(42,),
            exc_info=None,
        )
        result = filter_obj.filter(record)
        assert result is True  # Filter passes through


class TestMaskException:
    """Tests for mask_exception function."""

    def test_masks_exception_message(self):
        """Exception message should be masked."""
        original = ValueError("Error with api_key=secret123")
        masked = mask_exception(original)
        assert "secret123" not in str(masked)
        assert "***" in str(masked)
        assert isinstance(masked, ValueError)

    def test_preserves_exception_type(self):
        """Original exception type should be preserved."""
        original = RuntimeError("Something failed with token=abc123")
        masked = mask_exception(original)
        assert type(masked) is RuntimeError

    def test_preserves_exception_args(self):
        """Exception args should be scrubbed."""
        original = Exception("api_key=secret", "other_arg")
        masked = mask_exception(original)
        assert "secret" not in str(masked)
        assert "api_key" in str(masked) or "***" in str(masked)

    def test_handles_exception_without_args(self):
        """Exception without args should be handled."""
        original = Exception()
        masked = mask_exception(original)
        assert isinstance(masked, Exception)


class TestSensitivePatterns:
    """Tests for SENSITIVE_PATTERNS regex compilation."""

    def test_all_patterns_compile(self):
        """All patterns should compile successfully."""
        import re
        for name, pattern in SENSITIVE_PATTERNS.items():
            assert isinstance(pattern, re.Pattern), f"Pattern {name} should be compiled"

    def test_patterns_match_expected_inputs(self):
        """Patterns should match their intended inputs."""
        import re
        test_cases = [
            ("api_key", "api_key=secret123"),
            ("apikey", "apikey=secret123"),
            ("api-key", "api-key=secret123"),
            ("token", "token=abc.def.ghi"),
            ("secret", "secret=mysecret"),
            ("password", "password=mypass123"),
            ("bearer", "Bearer eyJhbGci"),
            ("basic_auth", "Basic dXNlcjpwYXNz"),
        ]
        for pattern_name, test_input in test_cases:
            pattern = SENSITIVE_PATTERNS.get(pattern_name)
            if pattern:
                assert pattern.search(test_input), f"Pattern {pattern_name} should match {test_input}"
