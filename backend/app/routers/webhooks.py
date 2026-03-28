"""
Webhook handlers for external service integrations (Typeform NPS survey, etc.)
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from sqlalchemy import insert, select
from app.db import get_db
from app.models import NPSResponse, User
import logging
import os

logger = logging.getLogger(__name__)
router = APIRouter()


class TypeformNPSPayload(BaseModel):
    """Typeform webhook NPS response schema"""

    form_id: str
    event_id: str
    event_type: str
    timestamp: str
    data: dict


class NPSResponseRequest(BaseModel):
    """Direct NPS response submission"""

    user_id: str
    score: int  # 0-10
    feedback: str = None


@router.post("/webhooks/nps-response")
async def receive_nps_response(payload: TypeformNPSPayload):
    """
    Receive NPS responses from Typeform webhook.

    Typeform sends this data:
    {
        "form_id": "abc123",
        "event_id": "evt_123",
        "event_type": "form_response",
        "timestamp": "2026-03-28T15:30:00Z",
        "data": {
            "response": {
                "submitted_at": "2026-03-28T15:30:00Z",
                "answers": [
                    {"field": {"id": "nps_score"}, "number": 9},
                    {"field": {"id": "feedback"}, "text": "Great product!"},
                    {"field": {"id": "email"}, "email": "user@example.com"}
                ]
            }
        }
    }
    """
    try:
        if payload.event_type != "form_response":
            return {"status": "ignored", "reason": "not a form_response"}

        # Extract NPS data from Typeform response
        response_data = payload.data.get("response", {})
        answers = response_data.get("answers", [])

        nps_score = None
        feedback_text = None
        user_email = None

        # Parse answers
        for answer in answers:
            field_id = answer.get("field", {}).get("id")

            if field_id == "nps_score":
                nps_score = answer.get("number")
            elif field_id == "feedback":
                feedback_text = answer.get("text")
            elif field_id == "email":
                user_email = answer.get("email")

        # Validate score
        if nps_score is None or not (0 <= nps_score <= 10):
            logger.warning(f"Invalid NPS score: {nps_score}")
            raise HTTPException(400, "Invalid NPS score (0-10 required)")

        # Find user by email
        async with get_db() as conn:
            user = await conn.execute(
                select(User).where(User.email == user_email)
            )
            user_record = user.scalar_one_or_none()

            if not user_record:
                logger.warning(f"NPS response for unknown user: {user_email}")
                # Still log the response even if user not found
                user_id = None
            else:
                user_id = user_record.id

            # Store NPS response
            nps_response = insert(NPSResponse).values(
                user_id=user_id,
                user_email=user_email,
                score=nps_score,
                feedback=feedback_text,
                received_at=datetime.fromisoformat(payload.timestamp),
                responded_at=datetime.fromisoformat(
                    response_data.get("submitted_at", payload.timestamp)
                ),
            )

            await conn.execute(nps_response)
            await conn.commit()

        # Log response
        logger.info(
            f"nps.response",
            extra={
                "email": user_email,
                "score": nps_score,
                "has_feedback": bool(feedback_text),
            },
        )

        # Classify (promoter, passive, detractor)
        if nps_score >= 9:
            classification = "promoter"
        elif nps_score >= 7:
            classification = "passive"
        else:
            classification = "detractor"

        return {
            "status": "ok",
            "user_email": user_email,
            "score": nps_score,
            "classification": classification,
        }

    except Exception as e:
        logger.error(f"nps.webhook.error", extra={"error": str(e)})
        raise HTTPException(500, f"Failed to process NPS response: {str(e)}")


@router.post("/webhooks/nps-response-direct")
async def submit_nps_response_direct(request: NPSResponseRequest):
    """
    Direct NPS submission endpoint (for in-app surveys).

    Usage:
    POST /webhooks/nps-response-direct
    {
        "user_id": "user-uuid",
        "score": 8,
        "feedback": "Love the recommendations!"
    }
    """
    try:
        # Validate score
        if not (0 <= request.score <= 10):
            raise HTTPException(400, "Score must be 0-10")

        async with get_db() as conn:
            # Create NPS response
            nps_response = insert(NPSResponse).values(
                user_id=request.user_id,
                score=request.score,
                feedback=request.feedback,
                responded_at=datetime.utcnow(),
            )

            await conn.execute(nps_response)
            await conn.commit()

        logger.info(
            f"nps.direct.response",
            extra={"user_id": request.user_id, "score": request.score},
        )

        return {"status": "ok", "score": request.score}

    except Exception as e:
        logger.error(f"nps.direct.error", extra={"error": str(e)})
        raise HTTPException(500, f"Failed to submit NPS response: {str(e)}")


@router.get("/webhooks/nps-summary")
async def get_nps_summary():
    """
    Get NPS summary statistics.

    Returns:
    {
        "total_responses": 42,
        "average_score": 7.8,
        "nps_score": 35,  # (promoters - detractors) / total * 100
        "promoters": 25,  # score 9-10
        "passives": 12,   # score 7-8
        "detractors": 5   # score 0-6
    }
    """
    try:
        async with get_db() as conn:
            # Get all responses
            result = await conn.execute(select(NPSResponse))
            responses = result.scalars().all()

            if not responses:
                return {
                    "total_responses": 0,
                    "average_score": None,
                    "nps_score": None,
                    "promoters": 0,
                    "passives": 0,
                    "detractors": 0,
                }

            scores = [r.score for r in responses]
            total = len(scores)

            promoters = sum(1 for s in scores if s >= 9)
            passives = sum(1 for s in scores if 7 <= s < 9)
            detractors = sum(1 for s in scores if s < 7)

            avg_score = sum(scores) / total
            nps = ((promoters - detractors) / total * 100) if total > 0 else 0

            return {
                "total_responses": total,
                "average_score": round(avg_score, 1),
                "nps_score": round(nps, 1),
                "promoters": promoters,
                "passives": passives,
                "detractors": detractors,
            }

    except Exception as e:
        logger.error(f"nps.summary.error", extra={"error": str(e)})
        raise HTTPException(500, "Failed to calculate NPS summary")
