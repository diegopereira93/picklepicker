"""Paddles API endpoints."""

import logging
from typing import Optional
from fastapi import APIRouter, Query, HTTPException, status
from psycopg.rows import dict_row
from app.schemas import (
    PaddleResponse,
    PaddleListResponse,
    PriceHistoryResponse,
    LatestPriceResponse,
    HealthResponse,
    SpecsResponse,
    PriceSnapshot,
)
from app.db import get_connection

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/paddles", tags=["paddles"])


@router.get("", response_model=PaddleListResponse, status_code=status.HTTP_200_OK)
async def list_paddles(
    brand: Optional[str] = Query(None, description="Filter by brand"),
    model_slug: Optional[str] = Query(None, description="Filter by model slug"),
    price_min: Optional[float] = Query(None, description="Min price BRL"),
    price_max: Optional[float] = Query(None, description="Max price BRL"),
    in_stock: Optional[bool] = Query(None, description="Only in-stock items"),
    limit: int = Query(50, ge=1, le=100, description="Pagination limit"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    """List all paddles with optional filters."""
    # Build SQL with WHERE clauses based on filters
    # Note: dedup_status column may not exist in all schemas, so we omit it
    where_clauses = ["1=1"]  # Always true placeholder
    params = []

    if brand:
        where_clauses.append("LOWER(brand) = LOWER(%s)")
        params.append(brand)
    if model_slug:
        where_clauses.append("model_slug = %s")
        params.append(model_slug)
    if price_min:
        where_clauses.append("price_min_brl >= %s")
        params.append(price_min)
    if price_max:
        where_clauses.append("price_min_brl <= %s")
        params.append(price_max)
    if in_stock is not None:
        where_clauses.append("in_stock = %s")
        params.append(in_stock)

    where = " AND ".join(where_clauses)

    async with get_connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            # Count query
            count_query = f"SELECT COUNT(*) as total FROM paddles WHERE {where}"
            await cur.execute(count_query, params)
            count_result = await cur.fetchone()
            total = count_result["total"] if count_result else 0

            # Data query with pagination - include specs, skill_level, in_stock, model_slug
            data_query = f"""
                SELECT p.id, p.name, p.brand, p.manufacturer_sku as sku, p.image_url, p.price_min_brl, p.created_at,
                       p.model_slug, p.skill_level, p.in_stock,
                       ps.swingweight, ps.twistweight, ps.weight_oz, ps.core_thickness_mm, ps.face_material
                FROM paddles p
                LEFT JOIN paddle_specs ps ON p.id = ps.paddle_id
                WHERE {where}
                ORDER BY p.created_at DESC
                LIMIT %s OFFSET %s
            """
            await cur.execute(data_query, params + [limit, offset])
            paddles = await cur.fetchall()

    items = [
        PaddleResponse(
            id=p.get("id", 0),
            name=p.get("name", ""),
            brand=p.get("brand", ""),
            sku=p.get("sku"),
            image_url=p.get("image_url"),
            price_min_brl=p.get("price_min_brl"),
            created_at=p.get("created_at"),
            model_slug=p.get("model_slug"),
            skill_level=p.get("skill_level"),
            in_stock=p.get("in_stock"),
            specs=SpecsResponse(
                swingweight=p.get("swingweight"),
                twistweight=p.get("twistweight"),
                weight_oz=p.get("weight_oz"),
                core_thickness_mm=p.get("core_thickness_mm"),
                face_material=p.get("face_material"),
            ) if any([p.get("swingweight"), p.get("twistweight"), p.get("weight_oz"), p.get("core_thickness_mm"), p.get("face_material")]) else None,
        )
        for p in paddles
    ]
    return PaddleListResponse(items=items, total=total, limit=limit, offset=offset)


@router.get("/{paddle_id}", response_model=PaddleResponse, status_code=status.HTTP_200_OK)
async def get_paddle(paddle_id: int):
    """Get single paddle with full details."""
    query = """
    SELECT p.id, p.name, p.brand, p.manufacturer_sku as sku, p.image_url, p.price_min_brl, p.created_at,
           ps.swingweight, ps.twistweight, ps.weight_oz, ps.core_thickness_mm, ps.face_material
    FROM paddles p
    LEFT JOIN paddle_specs ps ON p.id = ps.paddle_id
    WHERE p.id = %s
    """
    async with get_connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(query, [paddle_id])
            paddle = await cur.fetchone()

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
        id=paddle.get("id", 0),
        name=paddle.get("name", ""),
        brand=paddle.get("brand", ""),
        sku=paddle.get("sku"),
        image_url=paddle.get("image_url"),
        specs=specs,
        price_min_brl=paddle.get("price_min_brl"),
        created_at=paddle.get("created_at"),
    )


@router.get("/{paddle_id}/prices", response_model=PriceHistoryResponse, status_code=status.HTTP_200_OK)
async def get_paddle_prices(paddle_id: int):
    """Get price history for a paddle across all retailers."""
    async with get_connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            # Verify paddle exists
            query = "SELECT id, name FROM paddles WHERE id = %s"
            await cur.execute(query, [paddle_id])
            paddle = await cur.fetchone()
            if not paddle:
                raise HTTPException(status_code=404, detail="Paddle not found")

            # Get prices
            prices_query = """
            SELECT r.name AS retailer_name, ps.price_brl, ps.currency, ps.in_stock, ps.scraped_at
            FROM price_snapshots ps
            JOIN retailers r ON ps.retailer_id = r.id
            WHERE ps.paddle_id = %s
            ORDER BY ps.scraped_at DESC
            """
            await cur.execute(prices_query, [paddle_id])
            prices = await cur.fetchall()

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
        paddle_name=paddle.get("name", ""),
        prices=price_items,
    )


@router.get("/{paddle_id}/latest-prices", response_model=LatestPriceResponse, status_code=status.HTTP_200_OK)
async def get_paddle_latest_prices(paddle_id: int):
    """Get latest price from each retailer for a paddle."""
    async with get_connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            # Verify paddle exists
            query = "SELECT id, name FROM paddles WHERE id = %s"
            await cur.execute(query, [paddle_id])
            paddle = await cur.fetchone()
            if not paddle:
                raise HTTPException(status_code=404, detail="Paddle not found")

            # Get latest prices (from materialized view)
            prices_query = """
            SELECT r.name AS retailer_name, lp.price_brl, lp.currency, lp.in_stock, lp.scraped_at
            FROM latest_prices lp
            JOIN retailers r ON lp.retailer_id = r.id
            WHERE lp.paddle_id = %s
            """
            await cur.execute(prices_query, [paddle_id])
            prices = await cur.fetchall()

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
        paddle_name=paddle.get("name", ""),
        latest_prices=price_items,
    )


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health():
    """Health check endpoint."""
    return HealthResponse(status="ok")
