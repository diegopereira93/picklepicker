import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pipeline.crawlers.mercado_livre import (
    build_affiliate_url,
    search_pickleball_paddles,
    save_ml_items_to_db,
    run_mercado_livre_crawler,
    ML_SEARCH_URL,
)


class TestAffiliateUrl:
    def test_affiliate_url_tagged(self):
        """Affiliate tag appended as matt_id parameter."""
        url = build_affiliate_url(
            "https://www.mercadolivre.com.br/raquete-pickleball-selkirk-MLB12345",
            "MY_TAG"
        )
        assert "matt_id=MY_TAG" in url
        assert url.startswith("https://www.mercadolivre.com.br/raquete-pickleball-selkirk-MLB12345")

    def test_affiliate_url_with_existing_params(self):
        """Uses & separator when URL already has query params."""
        url = build_affiliate_url(
            "https://www.mercadolivre.com.br/product?variant=1",
            "MY_TAG"
        )
        assert "?variant=1&matt_id=MY_TAG" in url
        # Must not have double ?
        assert url.count("?") == 1

    def test_affiliate_url_empty_tag_returns_plain(self):
        """Empty affiliate tag returns permalink unchanged."""
        permalink = "https://www.mercadolivre.com.br/product-MLB99"
        url = build_affiliate_url(permalink, "")
        assert url == permalink


class TestSearch:
    async def test_search_returns_items(self, mock_ml_search_response):
        """ML search API returns items with expected fields."""
        mock_response = AsyncMock()
        mock_response.json.return_value = mock_ml_search_response
        mock_response.raise_for_status = MagicMock()

        with patch("pipeline.crawlers.mercado_livre.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            result = await search_pickleball_paddles(limit=50, offset=0)

            mock_client.get.assert_called_once()
            call_args = mock_client.get.call_args
            assert ML_SEARCH_URL in str(call_args)
            assert result["results"][0]["id"] == "MLB12345"


class TestDbPersistence:
    async def test_saves_to_db(self, mock_ml_search_response, mock_db_connection):
        """Items saved to price_snapshots with correct retailer_id and affiliate_url."""
        items = mock_ml_search_response["results"]

        # Mock execute to return a result with a fetchone for paddle insert
        execute_result = AsyncMock()
        execute_result.fetchone = AsyncMock(return_value=(1,))
        mock_db_connection.execute.return_value = execute_result

        saved = await save_ml_items_to_db(items, "TEST_TAG", mock_db_connection)

        assert saved == 2
        # Verify execute was called multiple times (paddle inserts + price_snapshot inserts)
        assert mock_db_connection.execute.call_count >= 2

        # Verify affiliate_url with tag appears in the calls
        all_calls_str = str(mock_db_connection.execute.call_args_list)
        assert "matt_id=TEST_TAG" in all_calls_str


class TestPagination:
    async def test_pagination(self):
        """Fetches multiple pages when total > limit."""
        page1 = {
            "results": [{"id": f"MLB{i}", "title": f"Paddle {i}", "price": 100.0,
                         "currency_id": "BRL", "available_quantity": 1,
                         "thumbnail": "https://img.com/1.jpg",
                         "permalink": f"https://ml.com/{i}", "condition": "new"}
                        for i in range(50)],
            "paging": {"total": 75, "offset": 0, "limit": 50}
        }
        page2 = {
            "results": [{"id": f"MLB{i}", "title": f"Paddle {i}", "price": 100.0,
                         "currency_id": "BRL", "available_quantity": 1,
                         "thumbnail": "https://img.com/2.jpg",
                         "permalink": f"https://ml.com/{i}", "condition": "new"}
                        for i in range(50, 75)],
            "paging": {"total": 75, "offset": 50, "limit": 50}
        }

        mock_resp1 = AsyncMock()
        mock_resp1.json.return_value = page1
        mock_resp1.raise_for_status = MagicMock()
        mock_resp2 = AsyncMock()
        mock_resp2.json.return_value = page2
        mock_resp2.raise_for_status = MagicMock()

        with patch("pipeline.crawlers.mercado_livre.httpx.AsyncClient") as mock_client_cls:
            mock_client = AsyncMock()
            mock_client.get = AsyncMock(side_effect=[mock_resp1, mock_resp2])
            mock_client_cls.return_value.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client_cls.return_value.__aexit__ = AsyncMock(return_value=False)

            all_items = await search_pickleball_paddles(limit=50, offset=0, fetch_all=True)
            assert mock_client.get.call_count == 2
            assert len(all_items["results"]) == 75


class TestPartialData:
    async def test_partial_data_skipped(self, mock_db_connection):
        """Items with missing or zero price are skipped."""
        items = [
            {"id": "MLB1", "title": "Good Paddle", "price": 999.90, "currency_id": "BRL",
             "available_quantity": 5, "thumbnail": "https://img.com/1.jpg",
             "permalink": "https://ml.com/1", "condition": "new"},
            {"id": "MLB2", "title": "No price paddle", "price": None, "currency_id": "BRL",
             "available_quantity": 0, "thumbnail": "https://img.com/2.jpg",
             "permalink": "https://ml.com/2", "condition": "new"},
            {"id": "MLB3", "title": "Zero price paddle", "price": 0, "currency_id": "BRL",
             "available_quantity": 1, "thumbnail": "https://img.com/3.jpg",
             "permalink": "https://ml.com/3", "condition": "new"},
        ]

        execute_result = AsyncMock()
        execute_result.fetchone = AsyncMock(return_value=(1,))
        mock_db_connection.execute.return_value = execute_result

        saved = await save_ml_items_to_db(items, "TAG", mock_db_connection)
        assert saved == 1  # only MLB1 saved
