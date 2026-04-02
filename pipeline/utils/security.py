"""Security utilities for sensitive data scrubbing and masking.

This module provides functions and classes for removing sensitive information
from strings, log messages, and exceptions before they are logged or transmitted.
"""

import re
import logging
from typing import Pattern


# Pre-compiled regex patterns for common sensitive data formats
SENSITIVE_PATTERNS: dict[str, Pattern] = {
    # API key variants
    "api_key": re.compile(r"(api[_-]?key\s*=\s*)([^\s&]+)", re.IGNORECASE),
    "apikey": re.compile(r"(apikey\s*=\s*)([^\s&]+)", re.IGNORECASE),

    # Generic key= pattern (catches fc-, sk-, etc. prefixes)
    "generic_key": re.compile(r"(\bkey\s*=\s*)([^\s&]+)", re.IGNORECASE),

    # Token variants
    "token": re.compile(r"(token\s*=\s*)([^\s&]+)", re.IGNORECASE),
    "bearer_token": re.compile(r"(Bearer\s+)([A-Za-z0-9_\-\.]+)", re.IGNORECASE),

    # Secret variants - match "secret=" or "secret_key=" or "secret-key="
    "secret": re.compile(r"(\bsecret(?:[_-]key)?\s*=\s*)([^\s&]+)", re.IGNORECASE),

    # Password
    "password": re.compile(r"(password\s*=\s*)([^\s&]+)", re.IGNORECASE),

    # Basic auth in URLs
    "basic_auth_url": re.compile(r"(://[^:]+:)([^@]+)(@)"),

    # Generic auth header patterns
    "authorization_basic": re.compile(r"(Basic\s+)([A-Za-z0-9+/=]+)", re.IGNORECASE),

    # URL query parameters with sensitive keys
    "url_token": re.compile(r"([?&](?:token|access_token|auth_token|api_key|apikey|key)=)([^&]*)", re.IGNORECASE),
}


def scrub_sensitive_data(text: str | None, replacement: str = "***") -> str:
    """Scrub sensitive data from text using regex patterns.

    Args:
        text: The text to scrub. None will be treated as empty string.
        replacement: String to replace sensitive values with. Defaults to "***".

    Returns:
        Text with sensitive values replaced.

    Examples:
        >>> scrub_sensitive_data("Error: api_key=sk-abc123")
        'Error: api_key=***'
        >>> scrub_sensitive_data("url?token=secret&other=value")
        'url?token=***&other=value'
    """
    if text is None:
        return ""

    result = text
    for pattern in SENSITIVE_PATTERNS.values():
        # Use lambda to preserve the group structure, replacing only the value
        def replace_match(match: re.Match) -> str:
            if len(match.groups()) >= 2:
                # Pattern has key/value groups
                return f"{match.group(1)}{replacement}"
            return replacement

        result = pattern.sub(replace_match, result)

    return result


class SensitiveDataFilter(logging.Filter):
    """Logging filter that scrubs sensitive data from log messages.

    Attach this filter to loggers to automatically scrub sensitive data
    from all log messages.

    Example:
        logger = logging.getLogger(__name__)
        logger.addFilter(SensitiveDataFilter())
    """

    def __init__(self, replacement: str = "***"):
        """Initialize the filter with replacement string.

        Args:
            replacement: String to replace sensitive values with.
        """
        super().__init__()
        self.replacement = replacement

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log record by scrubbing sensitive data.

        Args:
            record: The log record to filter.

        Returns:
            True to keep the record, False to drop it. Always returns True.
        """
        # Scrub the message
        if isinstance(record.msg, str):
            record.msg = scrub_sensitive_data(record.msg, self.replacement)

        # Scrub any string args
        if record.args:
            scrubbed_args = []
            for arg in record.args:
                if isinstance(arg, str):
                    scrubbed_args.append(scrub_sensitive_data(arg, self.replacement))
                else:
                    scrubbed_args.append(arg)
            record.args = tuple(scrubbed_args)

        return True


def mask_exception(exception: Exception, replacement: str = "***") -> Exception:
    """Create a new exception with sensitive data scrubbed from message.

    Preserves the original exception type where possible. The new exception
    will have the same type and scrubbed message/args.

    Args:
        exception: The original exception to mask.
        replacement: String to replace sensitive values with.

    Returns:
        New exception with scrubbed message.

    Example:
        >>> try:
        ...     raise ValueError("api_key=secret123 failed")
        ... except Exception as e:
        ...     safe_e = mask_exception(e)
        ...     raise safe_e
    """
    exc_type = type(exception)
    exc_str = str(exception)
    scrubbed_str = scrub_sensitive_data(exc_str, replacement)

    # Try to preserve args
    if exception.args:
        scrubbed_args = tuple(
            scrub_sensitive_data(str(arg), replacement) if isinstance(arg, str) else arg
            for arg in exception.args
        )
        try:
            return exc_type(*scrubbed_args)
        except Exception:
            # If creating with args fails, fall back to string-based creation
            pass

    # Create from string
    try:
        return exc_type(scrubbed_str)
    except Exception:
        # If even that fails, wrap in generic Exception
        return Exception(scrubbed_str)
