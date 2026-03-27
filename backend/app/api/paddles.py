"""Paddles API endpoints."""

import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from backend.app.schemas import (
    PaddleResponse,
    PaddleListResponse,
    PriceHistoryResponse,
    LatestPriceResponse,
    HealthResponse,
    SpecsResponse,
    PriceSnapshot,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/paddles", tags=["paddles"])

# Mock database functions (will be replaced with real DB calls)
async def db_fetch_all(query: str, params: list):
    """Fetch all rows (mock implementation)."""
    # This will be implemented when DB connection is available
    return []


async def db_fetch_one(query: str, params: list):
    """Fetch single row (mock implementation)."""
    # This will be implemented when DB connection is available
    return None


@router.get("", response_model=PaddleListResponse, status_code=status.HTTP_200_OK)
async def list_paddles(
    brand: Optional[str] = Query(None, description="Filter by brand"),
    price_min: Optional[float] = Query(None, description="Min price BRL"),
    price_max: Optional[float] = Query(None, description="Max price BRL"),
    in_stock: Optional[bool] = Query(None, description="Only in-stock items"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    """List all paddles with optional filters."""
    # Build SQL with WHERE clauses based on filters
    where_clauses = ["dedup_status IN ('pending', 'merged')"]
    params = []

    if brand:
        where_clauses.append(f"brand = ${len(params)+1}")
        params.append(brand)
    if price_min:
        where_clauses.append(f"price_min_brl >= ${len(params)+1}")
        params.append(price_min)
    if price_max:
        where_clauses.append(f"price_min_brl <= ${len(params)+1}")
        params.append(price_max)
    if in_stock is not None:
        where_clauses.append(f"in_stock = ${len(params)+1}")
        params.append(in_stock)

    where = " AND ".join(where_clauses)

    # Count query
    count_query = f"SELECT COUNT(*) as total FROM paddles WHERE {where}"
    count_result = await db_fetch_one(count_query, params)
    total = count_result["total"] if count_result else 0

    # Data query with pagination
    data_query = f"SELECT id, name, brand, sku, image_url, price_min_brl, created_at FROM paddles WHERE {where} ORDER BY created_at DESC LIMIT ${len(params)+1} OFFSET ${len(params)+2}"
    paddles = await db_fetch_all(data_query, params + [limit, offset])

    items = [
        PaddleResponse(
            id=p.get("id", 0),
            name=p.get("name", ""),
            brand=p.get("brand", ""),
            sku=p.get("sku"),
            image_url=p.get("image_url"),
            price_min_brl=p.get("price_min_brl"),
            created_at=p.get("created_at"),
        )
        for p in paddles
    ]
    return PaddleListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{paddle_id}", response_model=PaddleResponse, status_code=status.HTTP_200_OK)
async def get_paddle(paddle_id: int):
    """Get single paddle with full details."""
    query = """
    SELECT p.id, p.name, p.brand, p.sku, p.image_url, p.price_min_brl, p.created_at,
           ps.swingweight, ps.twistweight, ps.weight_oz, ps.core_thickness_mm, ps.face_material
    FROM paddles p
    LEFT JOIN paddle_specs ps ON p.id = ps.paddle_id
    WHERE p.id = $1 AND p.dedup_status IN ('pending', 'merged')
    """
    paddle = await db_fetch_one(query, [paddle_id])
    if not paddle:
        raise HTTPException(status_code=404, detail="Paddle not found")

    # Combine specs
    specs_data = {
        "swingweight": paddle.get("swingweight"),
        "twistweight": paddle.get("twistweight"),
        "weight_oz": paddle.get("weight_oz"),
        "core_thickness_mm": paddle.get("core_thickness_mm"),
        "face_material": paddle.get("face_material"),
    }
    specs = SpecsResponse(**specs_data) if any(specs_data.values()) else None

    return PaddleResponse(
        id=paddle["id"],
        name=paddle["name"],
        brand=paddle["brand"],
        sku=paddle.get("sku"),
        image_url=paddle.get("image_url"),
        specs=specs,
        price_min_brl=paddle.get("price_min_brl"),
        created_at=paddle["created_at"],
    )


@router.get("/{paddle_id}/prices", response_model=PriceHistoryResponse, status_code=status.HTTP_200_OK)
async def get_paddle_prices(paddle_id: int):
    """Get price history for a paddle across all retailers."""
    # Verify paddle exists
    query = "SELECT id, name FROM paddles WHERE id = $1"
    paddle = await db_fetch_one(query, [paddle_id])
    if not paddle:
        raise HTTPException(status_code=404, detail="Paddle not found")

    # Get prices
    prices_query = """
    SELECT r.name AS retailer_name, ps.price_brl, ps.currency, ps.in_stock, ps.scraped_at
    FROM price_snapshots ps
    JOIN retailers r ON ps.retailer_id = r.id
    WHERE ps.paddle_id = $1
    ORDER BY ps.scraped_at DESC
    """
    prices = await db_fetch_all(prices_query, [paddle_id])

    price_items = [
        PriceSnapshot(
            retailer_name=p.get("retailer_name", ""),
            price_brl=p.get("price_brl", 0),
            currency=p.get("currency", "BRL"),
            in_stock=p.get("in_stock", False),
            scraped_at=p.get("scraped_at"),
        )
        for p in prices
    ]

    return PriceHistoryResponse(
        paddle_id=paddle_id,
        paddle_name=paddle["name"],
        prices=price_items,
    )


@router.get("/{paddle_id}/latest-prices", response_model=LatestPriceResponse, status_code=status.HTTP_200_OK)
async def get_paddle_latest_prices(paddle_id: int):
    """Get latest price from each retailer for a paddle."""
    # Verify paddle exists
    query = "SELECT id, name FROM paddles WHERE id = $1"
    paddle = await db_fetch_one(query, [paddle_id])
    if not paddle:
        raise HTTPException(status_code=404, detail="Paddle not found")

    # Get latest prices (from materialized view)
    prices_query = """
    SELECT r.name AS retailer_name, lp.price_brl, lp.currency, lp.in_stock, lp.scraped_at
    FROM latest_prices lp
    JOIN retailers r ON lp.retailer_id = r.id
    WHERE lp.paddle_id = $1
    """
    prices = await db_fetch_all(prices_query, [paddle_id])

    price_items = [
        PriceSnapshot(
            retailer_name=p.get("retailer_name", ""),
            price_brl=p.get("price_brl", 0),
            currency=p.get("currency", "BRL"),
            in_stock=p.get("in_stock", False),
            scraped_at=p.get("scraped_at"),
        )
        for p in prices
    ]

    return LatestPriceResponse(
        paddle_id=paddle_id,
        paddle_name=paddle["name"],
        latest_prices=price_items,
    )


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health():
    """Health check endpoint."""
    return HealthResponse(status="ok")
