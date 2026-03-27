"""Tests for embedding document generation and batch processing."""

import pytest
from pipeline.embeddings.document_generator import (
    generate_paddle_document,
    swingweight_to_description,
    twistweight_to_description,
    core_to_description,
)
from pipeline.embeddings.batch_embedder import batch_embed_paddles, re_embed_flagged_paddles


class TestDocumentGeneration:
    """Document generation tests."""

    def test_document_generation__contains_specs(self):
        """Test that generated document contains required specs."""
        paddle = {
            "name": "Vanguard",
            "brand": "Selkirk",
            "retailer": "Drop Shot Brasil",
            "price_min": 599.99,
            "specs": {
                "swingweight": 115,
                "twistweight": 90,
                "weight_oz": 8.0,
                "core_thickness_mm": 13,
                "face_material": "Polypropylene"
            }
        }

        doc = generate_paddle_document(paddle)

        # Check document contains brand and paddle name
        assert "Selkirk" in doc
        assert "Vanguard" in doc or "raquete" in doc
        # Check contains specs
        assert "115" in doc or "Swingweight" in doc.lower()
        assert "13" in doc
        # Check contains retailer and price
        assert "Drop Shot Brasil" in doc
        assert "599" in doc  # Check for price (allow rounding)

        # Check token count is reasonable (roughly words / 1.3)
        word_count = len(doc.split())
        assert 30 < word_count < 500, f"Document has {word_count} words, expected reasonable length"

    def test_document_generation__minimal_specs(self):
        """Test generation with minimal specs."""
        paddle = {
            "name": "Basic Paddle",
            "brand": "Generic",
            "retailer": "Store",
            "price_min": 100.0,
            "specs": {}
        }

        doc = generate_paddle_document(paddle)

        assert "Generic Basic Paddle" in doc
        assert "100.00" in doc
        assert "Store" in doc

    def test_swingweight_descriptions(self):
        """Test swingweight to description mapping."""
        assert "ágil" in swingweight_to_description(70).lower()
        assert "equilibra" in swingweight_to_description(90).lower()
        assert "pesado" in swingweight_to_description(110).lower() or "potênc" in swingweight_to_description(110).lower()

    def test_twistweight_descriptions(self):
        """Test twistweight to description mapping."""
        assert "Precisão" in twistweight_to_description(70)
        assert "Equilibrado" in twistweight_to_description(95)
        assert "tolerância" in twistweight_to_description(120)

    def test_core_descriptions(self):
        """Test core thickness to description mapping."""
        assert "rápida" in core_to_description(10)
        assert "equilíbrio" in core_to_description(12)
        assert "controle superior" in core_to_description(14)


@pytest.mark.asyncio
async def test_batch_embed__placeholder():
    """Placeholder test for batch embed (mocking later)."""
    result = await batch_embed_paddles(paddle_ids=[], batch_size=5)
    assert result["status"] == "success"
    assert "total_embedded" in result
    assert "tokens" in result
    assert "cost_usd" in result


@pytest.mark.asyncio
async def test_re_embed_flagged__placeholder():
    """Placeholder test for re-embedding (mocking later)."""
    result = await re_embed_flagged_paddles()
    assert result["status"] == "success"
    assert "total_re_embedded" in result or "total_embedded" in result
