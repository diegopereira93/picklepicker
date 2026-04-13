from fastapi import APIRouter, status, Request
from psycopg.rows import dict_row
from app.schemas import AffiliateClickCreate, AffiliateClickResponse
from app.db import get_connection

router = APIRouter(prefix="/affiliate-clicks", tags=["affiliate-clicks"])


@router.post("", response_model=AffiliateClickResponse, status_code=status.HTTP_201_CREATED)
async def log_affiliate_click(click: AffiliateClickCreate, request: Request):
    async with get_connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """INSERT INTO affiliate_clicks (paddle_id, retailer, source, campaign, medium, page, affiliate_url)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id, paddle_id, retailer, created_at""",
                [click.paddle_id, click.retailer, click.source, click.campaign, click.medium, click.page, click.affiliate_url]
            )
            row = await cur.fetchone()
            return AffiliateClickResponse(**dict(row))
