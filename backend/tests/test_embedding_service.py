import pytest
from unittest.mock import patch, MagicMock, AsyncMock
import httpx
from app.services.embedding import EmbeddingManager


@pytest.fixture
def embedding_manager():
    with patch.dict("os.environ", {
        "GEMINI_API_KEY": "test-gemini-key",
        "JINA_API_KEY": "test-jina-key",
        "EMBEDDING_PROVIDER": "gemini",
    }):
        return EmbeddingManager()


@pytest.fixture
def jina_embedding_manager():
    """EmbeddingManager configured to use Jina as primary provider."""
    with patch.dict("os.environ", {
        "GEMINI_API_KEY": "test-gemini-key",
        "JINA_API_KEY": "test-jina-key",
        "EMBEDDING_PROVIDER": "jina",
    }):
        return EmbeddingManager()


@pytest.fixture
def default_embedding_manager():
    """EmbeddingManager with default (auto) provider config."""
    with patch.dict("os.environ", {
        "GEMINI_API_KEY": "test-gemini-key",
        "JINA_API_KEY": "test-jina-key",
    }):
        return EmbeddingManager()


@pytest.fixture
def gemini_success_response():
    return {
        "embedding": {
            "values": [0.1] * 768
        }
    }


@pytest.fixture
def jina_success_response():
    return {
        "data": [{"embedding": [0.2] * 768}]
    }


class TestEmbeddingManager:

    def test_init_loads_api_keys(self, embedding_manager):
        assert embedding_manager._gemini_key == "test-gemini-key"
        assert embedding_manager._jina_key == "test-jina-key"

    def test_init_loads_provider_config(self, embedding_manager):
        assert embedding_manager._provider == "gemini"

    def test_default_provider_is_auto(self, default_embedding_manager):
        assert default_embedding_manager._provider == "auto"

    def test_jina_provider_config(self, jina_embedding_manager):
        assert jina_embedding_manager._provider == "jina"

    @pytest.mark.asyncio
    async def test_get_embedding_uses_gemini_first(self, embedding_manager, gemini_success_response):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = gemini_success_response
        mock_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            result = await embedding_manager.get_embedding("test query")

            assert len(result) == 768
            assert result[0] == 0.1
            mock_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_embedding_fallback_to_jina(self, embedding_manager, jina_success_response):
        gemini_error = httpx.HTTPStatusError(
            "Rate limited",
            request=MagicMock(),
            response=MagicMock(status_code=429)
        )

        mock_gemini_response = MagicMock()
        mock_gemini_response.raise_for_status.side_effect = gemini_error

        mock_jina_response = MagicMock()
        mock_jina_response.status_code = 200
        mock_jina_response.json.return_value = jina_success_response
        mock_jina_response.raise_for_status = MagicMock()

        call_count = 0

        async def mock_post(url, **kwargs):
            nonlocal call_count
            call_count += 1
            if "generativelanguage" in url:
                raise gemini_error
            return mock_jina_response

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            result = await embedding_manager.get_embedding("test query")

            assert len(result) == 768
            assert result[0] == 0.2
            assert call_count == 2

    @pytest.mark.asyncio
    async def test_get_embedding_raises_when_both_fail(self, embedding_manager):
        """When both providers fail, uses zero vector fallback."""
        error = httpx.HTTPStatusError(
            "Error",
            request=MagicMock(),
            response=MagicMock(status_code=500)
        )

        with patch("httpx.AsyncClient.post", side_effect=error):
            result = await embedding_manager.get_embedding("test query")
            # Should return zero vector fallback
            assert isinstance(result, list)
            assert len(result) == 768
            assert all(x == 0.0 for x in result)

    @pytest.mark.asyncio
    async def test_empty_text_raises_error(self, embedding_manager):
        with pytest.raises(ValueError, match="vazio"):
            await embedding_manager.get_embedding("")

        with pytest.raises(ValueError, match="vazio"):
            await embedding_manager.get_embedding("   ")

    @pytest.mark.asyncio
    async def test_gemini_timeout_triggers_fallback(self, embedding_manager, jina_success_response):
        mock_jina_response = MagicMock()
        mock_jina_response.status_code = 200
        mock_jina_response.json.return_value = jina_success_response
        mock_jina_response.raise_for_status = MagicMock()

        async def mock_post(url, **kwargs):
            if "generativelanguage" in url:
                raise httpx.TimeoutException("Timeout")
            return mock_jina_response

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            result = await embedding_manager.get_embedding("test query")
            assert len(result) == 768

    @pytest.mark.asyncio
    async def test_default_uses_jina_priority(self, default_embedding_manager, jina_success_response):
        mock_jina_response = MagicMock()
        mock_jina_response.status_code = 200
        mock_jina_response.json.return_value = jina_success_response
        mock_jina_response.raise_for_status = MagicMock()

        with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_jina_response
            result = await default_embedding_manager.get_embedding("test query")

            assert len(result) == 768
            assert result[0] == 0.2
            mock_post.assert_called_once()
            call_url = mock_post.call_args[0][0]
            assert "jina.ai" in call_url

    @pytest.mark.asyncio
    async def test_jina_provider_skips_gemini(self, jina_embedding_manager, jina_success_response):
        mock_jina_response = MagicMock()
        mock_jina_response.status_code = 200
        mock_jina_response.json.return_value = jina_success_response
        mock_jina_response.raise_for_status = MagicMock()

        urls_called = []

        async def mock_post(url, **kwargs):
            urls_called.append(url)
            return mock_jina_response

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            result = await jina_embedding_manager.get_embedding("test query")

            assert len(result) == 768
            assert all("generativelanguage" not in u for u in urls_called)
            assert any("jina.ai" in u for u in urls_called)
