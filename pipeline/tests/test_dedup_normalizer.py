"""Tests for title normalization and tier-1/2 deduplication."""

import pytest
from unittest.mock import AsyncMock, patch
from pipeline.dedup.normalizer import (
    normalize_title,
    title_hash,
    tier1_match,
    tier2_match,
    get_or_create_paddle,
)


def test_normalize__removes_punctuation_and_spaces():
    """normalize_title: removes punctuation, normalizes spaces."""
    assert normalize_title("Selkirk Vanguard Power Air™") == "selkirk vanguard power air"
    assert normalize_title("JOOLA  Ben-Johns  Hyperion") == "joola benjohns hyperion"
    assert normalize_title("  Prolite  Radical  Pro  ") == "prolite radical pro"


def test_normalize__case_insensitive():
    """normalize_title: converts to lowercase."""
    assert normalize_title("SELKIRK VANGUARD") == "selkirk vanguard"
    assert normalize_title("Selkirk Vanguard") == "selkirk vanguard"
    assert normalize_title("selkirk vanguard") == "selkirk vanguard"


def test_normalize__handles_empty_and_special_chars():
    """normalize_title: handles edge cases."""
    assert normalize_title("") == ""
    assert normalize_title("   ") == ""
    assert normalize_title("Raquete™-Pickleball(®)") == "raquetepickleball"


def test_title_hash__consistent():
    """title_hash: same title always produces same hash."""
    title = "Selkirk Vanguard Power Air"
    hash1 = title_hash(title)
    hash2 = title_hash(title)
    assert hash1 == hash2


def test_title_hash__different_for_different_titles():
    """title_hash: different titles produce different hashes."""
    hash1 = title_hash("Selkirk Vanguard")
    hash2 = title_hash("JOOLA Ben Johns")
    assert hash1 != hash2


def test_title_hash__ignores_normalization():
    """title_hash: normalizes before hashing."""
    # "Selkirk Vanguard Power Air™" and "selkirk vanguard power air" should have same hash
    hash1 = title_hash("Selkirk Vanguard Power Air™")
    hash2 = title_hash("selkirk vanguard power air")
    assert hash1 == hash2


@pytest.mark.asyncio
async def test_tier1_match__finds_by_sku(mock_db_connection):
    """tier1_match: finds paddle by manufacturer SKU."""
    # Mock the result of execute().fetchone()
    result_mock = AsyncMock()
    result_mock.fetchone = AsyncMock(return_value=(42,))
    mock_db_connection.execute = AsyncMock(return_value=result_mock)

    with patch("pipeline.dedup.normalizer.get_connection") as mock_get_conn:
        mock_get_conn.return_value.__aenter__.return_value = mock_db_connection

        result = await tier1_match(sku="SELKIRK-12345", retailer_id=1)

        assert result == 42
        mock_db_connection.execute.assert_called_once()


@pytest.mark.asyncio
async def test_tier1_match__returns_none_if_not_found(mock_db_connection):
    """tier1_match: returns None if SKU not found."""
    result_mock = AsyncMock()
    result_mock.fetchone = AsyncMock(return_value=None)
    mock_db_connection.execute = AsyncMock(return_value=result_mock)

    with patch("pipeline.dedup.normalizer.get_connection") as mock_get_conn:
        mock_get_conn.return_value.__aenter__.return_value = mock_db_connection

        result = await tier1_match(sku="UNKNOWN-SKU", retailer_id=1)

        assert result is None


@pytest.mark.asyncio
async def test_tier1_match__handles_empty_sku(mock_db_connection):
    """tier1_match: returns None for empty/None SKU."""
    result = await tier1_match(sku="", retailer_id=1)
    assert result is None

    result = await tier1_match(sku=None, retailer_id=1)
    assert result is None


@pytest.mark.asyncio
async def test_tier2_match__finds_by_title_hash(mock_db_connection):
    """tier2_match: finds paddle by normalized title hash."""
    result_mock = AsyncMock()
    result_mock.fetchone = AsyncMock(return_value=(42,))
    mock_db_connection.execute = AsyncMock(return_value=result_mock)

    with patch("pipeline.dedup.normalizer.get_connection") as mock_get_conn:
        mock_get_conn.return_value.__aenter__.return_value = mock_db_connection

        result = await tier2_match(title="Selkirk Vanguard Power Air")

        assert result == 42
        mock_db_connection.execute.assert_called_once()


@pytest.mark.asyncio
async def test_tier2_match__returns_none_if_not_found(mock_db_connection):
    """tier2_match: returns None if title not found."""
    result_mock = AsyncMock()
    result_mock.fetchone = AsyncMock(return_value=None)
    mock_db_connection.execute = AsyncMock(return_value=result_mock)

    with patch("pipeline.dedup.normalizer.get_connection") as mock_get_conn:
        mock_get_conn.return_value.__aenter__.return_value = mock_db_connection

        result = await tier2_match(title="Unknown Paddle")

        assert result is None


@pytest.mark.asyncio
async def test_tier2_match__normalizes_title(mock_db_connection):
    """tier2_match: normalizes title before hashing."""
    result_mock = AsyncMock()
    result_mock.fetchone = AsyncMock(return_value=(42,))
    mock_db_connection.execute = AsyncMock(return_value=result_mock)

    with patch("pipeline.dedup.normalizer.get_connection") as mock_get_conn:
        mock_get_conn.return_value.__aenter__.return_value = mock_db_connection

        # These should find the same paddle due to normalization
        result1 = await tier2_match("Selkirk Vanguard Power Air™")
        result2 = await tier2_match("selkirk vanguard power air")

        # Both should have called execute with same hash
        calls = mock_db_connection.execute.call_args_list
        assert len(calls) == 2
        # Extract the hash values from the calls
        hash1 = calls[0][0][1]["hash"]
        hash2 = calls[1][0][1]["hash"]
        assert hash1 == hash2


@pytest.mark.asyncio
async def test_get_or_create_paddle__creates_if_not_exists(mock_db_connection):
    """get_or_create_paddle: creates new paddle if not found."""
    # First call: search returns None
    # Second call: insert returns paddle_id
    result_mock1 = AsyncMock()
    result_mock1.fetchone = AsyncMock(return_value=None)

    result_mock2 = AsyncMock()
    result_mock2.fetchone = AsyncMock(return_value=(99,))

    mock_db_connection.execute = AsyncMock(side_effect=[result_mock1, result_mock2])
    mock_db_connection.commit = AsyncMock()

    with patch("pipeline.dedup.normalizer.get_connection") as mock_get_conn:
        mock_get_conn.return_value.__aenter__.return_value = mock_db_connection

        result = await get_or_create_paddle(
            title="New Paddle",
            brand="TestBrand",
            specs={"weight_oz": 8.2}
        )

        assert result == 99
        # Should call execute twice: SELECT then INSERT
        assert mock_db_connection.execute.call_count == 2
        mock_db_connection.commit.assert_called_once()


@pytest.mark.asyncio
async def test_get_or_create_paddle__returns_existing(mock_db_connection):
    """get_or_create_paddle: returns existing paddle if found."""
    result_mock = AsyncMock()
    result_mock.fetchone = AsyncMock(return_value=(42,))
    mock_db_connection.execute = AsyncMock(return_value=result_mock)

    with patch("pipeline.dedup.normalizer.get_connection") as mock_get_conn:
        mock_get_conn.return_value.__aenter__.return_value = mock_db_connection

        result = await get_or_create_paddle(title="Existing Paddle")

        assert result == 42
        # Should only call execute once (SELECT)
        mock_db_connection.execute.assert_called_once()
        mock_db_connection.commit.assert_not_called()
