"""Response schemas for FastAPI endpoints."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class SpecsResponse(BaseModel):
    """Paddle specifications response model."""
    swingweight: Optional[float] = None
    twistweight: Optional[float] = None
    weight_oz: Optional[float] = None
    grip_size: Optional[str] = None
    core_thickness_mm: Optional[float] = None
    face_material: Optional[str] = None

    model_config = {"from_attributes": True}


class PaddleResponse(BaseModel):
    """Single paddle response with specs."""
    id: int
    name: str
    brand: str
    sku: Optional[str] = None
    image_url: Optional[str] = None
    specs: Optional[SpecsResponse] = None
    price_min_brl: Optional[float] = None
    created_at: Optional[datetime] = None
    model_slug: Optional[str] = None
    skill_level: Optional[str] = None
    in_stock: Optional[bool] = None

    model_config = {"from_attributes": True}


class PaddleListResponse(BaseModel):
    """Paginated list of paddles."""
    items: List[PaddleResponse]
    total: int
    limit: int
    offset: int


class PriceSnapshot(BaseModel):
    """Single price snapshot from a retailer."""
    retailer_name: str
    price_brl: float
    currency: str
    in_stock: bool
    scraped_at: datetime

    model_config = {"from_attributes": True}


class PriceHistoryResponse(BaseModel):
    """Historical price data for a paddle."""
    paddle_id: int
    paddle_name: str
    prices: List[PriceSnapshot]


class LatestPriceResponse(BaseModel):
    """Latest prices per retailer for a paddle."""
    paddle_id: int
    paddle_name: str
    latest_prices: List[PriceSnapshot]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
