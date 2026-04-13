from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from datetime import datetime
import structlog
import urllib.parse
from psycopg.rows import dict_row
from app.db import get_connection


logger = structlog.get_logger()
router = APIRouter()


@router.get("/track-affiliate")
async def track_affiliate(
    utm_source: str = "pickleiq",
    utm_campaign: str = "search",
    utm_medium: str = "chat",
    paddle_id: int = None,
    redirect_url: str = None
):
    """Track affiliate click and redirect to partner."""
    try:
        logger.info(
            "affiliate.click",
            utm_source=utm_source,
            utm_campaign=utm_campaign,
            utm_medium=utm_medium,
            paddle_id=paddle_id,
            redirect_url=redirect_url
        )

        try:
            async with get_connection() as conn:
                async with conn.cursor(row_factory=dict_row) as cur:
                    await cur.execute(
                        """INSERT INTO affiliate_clicks (paddle_id, source, campaign, medium, affiliate_url)
                           VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                        [paddle_id, utm_source, utm_campaign, utm_medium, redirect_url]
                    )
        except Exception:
            pass

        if redirect_url:
            decoded_url = urllib.parse.unquote(redirect_url)
            return RedirectResponse(url=decoded_url, status_code=302)
        else:
            raise HTTPException(status_code=400, detail="Missing redirect_url")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("affiliate.tracking.error", error=str(e))
        raise HTTPException(status_code=500, detail="Tracking failed")
