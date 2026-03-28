from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from datetime import datetime
import structlog
import urllib.parse


logger = structlog.get_logger()
router = APIRouter()


@router.get("/api/track-affiliate")
async def track_affiliate(
    utm_source: str = "pickleiq",
    utm_campaign: str = "search",
    utm_medium: str = "chat",
    paddle_id: int = None,
    redirect_url: str = None
):
    """Track affiliate click and redirect to partner."""
    try:
        # Log the click (database integration would go here)
        logger.info(
            "affiliate.click",
            utm_source=utm_source,
            utm_campaign=utm_campaign,
            utm_medium=utm_medium,
            paddle_id=paddle_id,
            redirect_url=redirect_url
        )

        # Redirect to partner
        if redirect_url:
            # Decode the URL if it was encoded
            decoded_url = urllib.parse.unquote(redirect_url)
            return RedirectResponse(url=decoded_url, status_code=302)
        else:
            raise HTTPException(status_code=400, detail="Missing redirect_url")
    except Exception as e:
        logger.error("affiliate.tracking.error", error=str(e))
        raise HTTPException(status_code=500, detail="Tracking failed")
