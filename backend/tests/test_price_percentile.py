"""Tests for P20 percentile calculation and is_good_time logic."""

import pytest
from backend.app.api.price_history import calculate_p20, group_prices_by_retailer


class TestPercentileCalculation:
    """Test P20 (20th percentile) calculation."""

    def test_p20_of_single_price(self):
        """P20 of a single price is that price itself."""
        assert calculate_p20([100.0]) == 100.0

    def test_p20_of_sorted_list(self):
        """P20 of [100, 200, 300, 400, 500] — index = floor(5 * 0.2) = 1 → 200."""
        prices = [100.0, 200.0, 300.0, 400.0, 500.0]
        result = calculate_p20(prices)
        assert result == 200.0

    def test_p20_sorts_input(self):
        """P20 should sort prices before calculating."""
        prices = [500.0, 100.0, 300.0, 200.0, 400.0]
        result = calculate_p20(prices)
        assert result == 200.0  # Same as sorted version

    def test_p20_of_two_prices(self):
        """P20 of two prices: index = floor(2 * 0.2) = 0 → first (lowest)."""
        prices = [100.0, 200.0]
        result = calculate_p20(prices)
        assert result == 100.0

    def test_p20_of_ten_prices(self):
        """P20 of 10 prices: index = floor(10 * 0.2) = 2 → third value."""
        prices = [10.0, 20.0, 30.0, 40.0, 50.0, 60.0, 70.0, 80.0, 90.0, 100.0]
        result = calculate_p20(prices)
        assert result == 30.0

    def test_p20_boundary_index_zero(self):
        """When index would be 0, returns the minimum price."""
        prices = [500.0]
        result = calculate_p20(prices)
        assert result == 500.0

    def test_p20_uses_decimal_precision(self):
        """P20 handles float prices correctly."""
        prices = [149.99, 199.99, 249.99, 299.99, 349.99]
        result = calculate_p20(prices)
        assert result == 199.99


class TestIsGoodTimeToBuy:
    """Test is_good_time flag logic (price <= P20)."""

    def test_price_equal_to_p20_is_good(self):
        """Price exactly at P20 is a good time to buy."""
        prices = [100.0, 200.0, 300.0, 400.0, 500.0]
        p20 = calculate_p20(prices)  # 200.0
        assert p20 == 200.0
        assert 200.0 <= p20  # is_good_time = True

    def test_price_below_p20_is_good(self):
        """Price below P20 is a good time to buy."""
        prices = [100.0, 200.0, 300.0, 400.0, 500.0]
        p20 = calculate_p20(prices)  # 200.0
        assert 150.0 <= p20  # is_good_time = True

    def test_price_above_p20_is_not_good(self):
        """Price above P20 is NOT a good time to buy."""
        prices = [100.0, 200.0, 300.0, 400.0, 500.0]
        p20 = calculate_p20(prices)  # 200.0
        assert not (250.0 <= p20)  # is_good_time = False

    def test_high_current_price_is_not_good(self):
        """Current price at the high end is not a good time."""
        prices = [100.0, 200.0, 300.0, 400.0, 500.0]
        p20 = calculate_p20(prices)  # 200.0
        assert not (500.0 <= p20)  # is_good_time = False


class TestGroupPricesByRetailer:
    """Test retailer grouping and P20 calculation per retailer."""

    def test_groups_single_retailer(self):
        """Rows from one retailer group together correctly."""
        from datetime import date
        rows = [
            {"retailer_name": "Mercado Livre", "price_brl": 100.0, "date": date(2025, 1, 1)},
            {"retailer_name": "Mercado Livre", "price_brl": 200.0, "date": date(2025, 1, 2)},
        ]
        result = group_prices_by_retailer(rows)
        assert len(result) == 2
        assert all(r["retailer"] == "Mercado Livre" for r in result)

    def test_groups_multiple_retailers_separately(self):
        """Rows from different retailers have separate P20 values."""
        from datetime import date
        rows = [
            {"retailer_name": "Mercado Livre", "price_brl": 100.0, "date": date(2025, 1, 1)},
            {"retailer_name": "Mercado Livre", "price_brl": 500.0, "date": date(2025, 1, 2)},
            {"retailer_name": "Brazil Pickleball", "price_brl": 200.0, "date": date(2025, 1, 1)},
            {"retailer_name": "Brazil Pickleball", "price_brl": 600.0, "date": date(2025, 1, 2)},
        ]
        result = group_prices_by_retailer(rows)
        assert len(result) == 4

        ml_items = [r for r in result if r["retailer"] == "Mercado Livre"]
        bp_items = [r for r in result if r["retailer"] == "Brazil Pickleball"]

        # P20 for ML: prices [100, 500] → index=0 → 100.0
        assert ml_items[0]["p20"] == 100.0
        # P20 for BP: prices [200, 600] → index=0 → 200.0
        assert bp_items[0]["p20"] == 200.0

    def test_is_good_time_flag_set_correctly(self):
        """is_good_time flag is True when price <= P20."""
        from datetime import date
        rows = [
            {"retailer_name": "Mercado Livre", "price_brl": 100.0, "date": date(2025, 1, 1)},
            {"retailer_name": "Mercado Livre", "price_brl": 200.0, "date": date(2025, 1, 2)},
            {"retailer_name": "Mercado Livre", "price_brl": 300.0, "date": date(2025, 1, 3)},
            {"retailer_name": "Mercado Livre", "price_brl": 400.0, "date": date(2025, 1, 4)},
            {"retailer_name": "Mercado Livre", "price_brl": 500.0, "date": date(2025, 1, 5)},
        ]
        result = group_prices_by_retailer(rows)
        # P20 = 200.0 (index 1 of sorted [100,200,300,400,500])
        for r in result:
            if r["price"] <= r["p20"]:
                assert r["is_good_time"] is True
            else:
                assert r["is_good_time"] is False

    def test_result_contains_all_required_fields(self):
        """Each result item has retailer, date, price, p20, is_good_time."""
        from datetime import date
        rows = [
            {"retailer_name": "Mercado Livre", "price_brl": 100.0, "date": date(2025, 1, 1)},
        ]
        result = group_prices_by_retailer(rows)
        assert len(result) == 1
        item = result[0]
        assert "retailer" in item
        assert "date" in item
        assert "price" in item
        assert "p20" in item
        assert "is_good_time" in item

    def test_date_is_iso_string(self):
        """date field in result is an ISO format string."""
        from datetime import date
        rows = [
            {"retailer_name": "ML", "price_brl": 100.0, "date": date(2025, 3, 15)},
        ]
        result = group_prices_by_retailer(rows)
        assert result[0]["date"] == "2025-03-15"

    def test_empty_rows_returns_empty_list(self):
        """Empty input returns empty list."""
        result = group_prices_by_retailer([])
        assert result == []
