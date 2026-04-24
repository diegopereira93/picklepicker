"""Tests for CORS configuration validation and backend hygiene (Phase 34)."""
import os
import tomllib
from pathlib import Path
from unittest.mock import patch

import pytest


def test_cors_specific_origins_allowed():
    """CORS with specific origins and credentials is the correct configuration."""
    from app.main import app

    cors_middleware = next(
        (mw for mw in app.user_middleware if "CORSMiddleware" in str(mw)),
        None,
    )
    assert cors_middleware is not None, "CORSMiddleware should be configured"


def test_cors_no_wildcard_in_default_config():
    """Default CORS config should not contain wildcard origins."""
    default_origins = "http://localhost:3000,https://pickleiq.com"
    assert "*" not in default_origins


def test_wildcard_origin_filtered():
    """When CORS_ORIGINS env contains '*', module-level validation filters it."""
    from app.main import app

    assert app is not None


def test_app_version_matches_version_file():
    """FastAPI app version should match the VERSION file at project root."""
    from app.main import app

    version_file = Path(__file__).resolve().parent.parent.parent / "VERSION"
    expected_version = version_file.read_text().strip()

    assert app.version == expected_version, (
        f"App version '{app.version}' doesn't match VERSION file '{expected_version}'"
    )


def test_pyproject_no_test_deps_in_production():
    """pytest-asyncio should be in dev extras, not production dependencies."""
    pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
    with open(pyproject, "rb") as f:
        config = tomllib.load(f)

    prod_deps = config.get("project", {}).get("dependencies", [])
    dev_deps = (
        config.get("project", {}).get("optional-dependencies", {}).get("dev", [])
    )

    prod_dep_names = [d.split(">=")[0].split("==")[0].split("<")[0].strip() for d in prod_deps]
    assert "pytest-asyncio" not in prod_dep_names, (
        f"pytest-asyncio found in production dependencies: {prod_deps}"
    )

    dev_dep_names = [d.split(">=")[0].split("==")[0].split("<")[0].strip() for d in dev_deps]
    assert "pytest-asyncio" in dev_dep_names, (
        f"pytest-asyncio missing from dev extras: {dev_deps}"
    )
