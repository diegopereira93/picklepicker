"""Admin API endpoints for review queue management.

Protected by Authorization: Bearer {ADMIN_SECRET} middleware.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from pipeline.dedup.review_queue import (
    get_review_queue_items,
    resolve_queue_item,
    dismiss_queue_item,
)

router = APIRouter(prefix="/admin", tags=["admin"])


class ReviewQueueItem(BaseModel):
    id: int
    type: str
    paddle_id: int
    related_paddle_id: int | None
    data: dict
    status: str
    created_at: str | None


class ResolveQueueItemRequest(BaseModel):
    action: str  # "merge", "reject", "manual", etc.
    decision_data: dict | None = None


class DismissQueueItemRequest(BaseModel):
    reason: str = ""


@router.get("/queue", response_model=list[ReviewQueueItem])
async def get_queue(
    type: str | None = Query(None, description="Filter by type (duplicate, spec_unmatched, price_anomaly)"),
    status: str = Query("pending", description="Filter by status"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    """Get review queue items.

    Query params:
    - type: Filter by queue type
    - status: Filter by status (pending, resolved, dismissed)
    - limit: Max items (default 50, max 500)
    - offset: Pagination offset

    Returns:
        List of review queue items
    """
    items = await get_review_queue_items(
        queue_type=type,
        status=status,
        limit=limit,
        offset=offset,
    )
    return items


@router.get("/queue/{queue_id}")
async def get_queue_item(queue_id: int):
    """Get single review queue item by ID."""
    items = await get_review_queue_items(limit=1, offset=0)
    # Filter to find the item
    for item in items:
        if item["id"] == queue_id:
            return item
    raise HTTPException(status_code=404, detail="Queue item not found")


@router.patch("/queue/{queue_id}/resolve")
async def resolve_item(queue_id: int, request: ResolveQueueItemRequest):
    """Resolve a review queue item.

    Body:
    {
      "action": "merge" | "reject" | "manual",
      "decision_data": { ... }
    }
    """
    success = await resolve_queue_item(
        queue_id=queue_id,
        action=request.action,
        resolved_by="admin",
        decision_data=request.decision_data or {},
    )

    if not success:
        raise HTTPException(status_code=404, detail="Queue item not found")

    return {"status": "resolved", "queue_id": queue_id, "action": request.action}


@router.patch("/queue/{queue_id}/dismiss")
async def dismiss_item(queue_id: int, request: DismissQueueItemRequest):
    """Dismiss a review queue item."""
    success = await dismiss_queue_item(queue_id=queue_id, reason=request.reason)

    if not success:
        raise HTTPException(status_code=404, detail="Queue item not found")

    return {"status": "dismissed", "queue_id": queue_id, "reason": request.reason}


@router.get("/paddles")
async def get_paddles(limit: int = Query(50, ge=1, le=500), offset: int = Query(0, ge=0)):
    """Get all paddles from catalog.

    Used for admin catalog browsing.
    """
    # This will be implemented in backend integration
    return {"paddles": [], "total": 0, "limit": limit, "offset": offset}


@router.patch("/paddles/{paddle_id}")
async def update_paddle(paddle_id: int):
    """Update paddle specs or metadata.

    Future endpoint for admin catalog management.
    """
    return {"status": "not_implemented"}
