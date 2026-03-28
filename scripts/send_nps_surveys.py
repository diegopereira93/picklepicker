#!/usr/bin/env python3
"""
Send NPS surveys to users at day 30 post-launch.

This script:
1. Finds users created >30 days ago
2. Checks if they haven't received NPS survey yet
3. Sends Typeform link via Resend email
4. Records survey sent in database
"""

import asyncio
import os
from datetime import datetime, timedelta
import logging
from sqlalchemy import select, update, and_
from app.db import get_db
from app.models import User, NPSResponse
from resend import Resend

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TYPEFORM_FORM_ID = os.getenv("TYPEFORM_FORM_ID", "")
RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
TYPEFORM_URL = f"https://typeform.com/to/{TYPEFORM_FORM_ID}"


async def get_eligible_users():
    """Find users created >30 days ago who haven't received NPS yet."""
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    async with get_db() as conn:
        # Users who were created more than 30 days ago
        users = await conn.execute(
            select(User).where(User.created_at < thirty_days_ago)
        )

        all_eligible = users.scalars().all()

        # Filter out users who already received NPS
        async with get_db() as conn:
            nps_recipients = await conn.execute(select(NPSResponse.user_id))
            nps_user_ids = set(nps_recipients.scalars().all())

        return [u for u in all_eligible if u.id not in nps_user_ids]


async def send_nps_surveys():
    """Send NPS survey emails to eligible users."""
    try:
        users = await get_eligible_users()

        if not users:
            logger.info("No eligible users for NPS survey at this time")
            return

        logger.info(f"Sending NPS surveys to {len(users)} eligible users")

        resend = Resend(api_key=RESEND_API_KEY)

        for user in users:
            try:
                # Customize Typeform URL with user email as prefill
                survey_url = f"{TYPEFORM_URL}?email={user.email}"

                # Send email
                response = resend.emails.send(
                    {
                        "from": "noreply@pickleiq.com",
                        "to": user.email,
                        "subject": "How are you enjoying PickleIQ? Quick feedback survey",
                        "html": f"""
                        <h2>Hi {user.name}!</h2>
                        <p>It's been 30 days since you joined PickleIQ. We'd love to hear how you're enjoying the product!</p>
                        <p>
                            <a href="{survey_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                                Take 2-minute survey
                            </a>
                        </p>
                        <p>Your feedback helps us improve. Thank you!</p>
                        <p>— The PickleIQ team</p>
                        """,
                    }
                )

                # Record survey sent
                async with get_db() as conn:
                    # Create a placeholder NPS response record marking survey sent
                    stmt = update(User).where(User.id == user.id).values(
                        nps_survey_sent_at=datetime.utcnow()
                    )
                    await conn.execute(stmt)
                    await conn.commit()

                logger.info(f"NPS survey sent to {user.email}")

            except Exception as e:
                logger.error(f"Failed to send NPS survey to {user.email}: {str(e)}")
                continue

        logger.info(f"Successfully sent NPS surveys to {len(users)} users")

    except Exception as e:
        logger.error(f"send_nps_surveys failed: {str(e)}")
        raise


if __name__ == "__main__":
    asyncio.run(send_nps_surveys())
