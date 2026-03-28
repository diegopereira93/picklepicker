"""Price alert worker.

Runs every 24h via GitHub Actions. Queries active price_alerts, fetches
current prices from latest_prices view, and sends emails via Resend when
current_price <= price_target. Idempotent: only triggers if last_triggered
is NULL or > 24h ago.
"""

import os
import asyncio
import logging
from datetime import datetime, timedelta, timezone

import httpx
import psycopg

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = "alerts@pickleiq.com"
RESEND_ENDPOINT = "https://api.resend.com/emails"
COOLDOWN_HOURS = 24


def _build_alert_email_html(
    paddle_name: str,
    current_price: float,
    price_target: float,
) -> str:
    return f"""
<html>
  <body>
    <h2>Raquete em promocao!</h2>
    <p>
      Boa noticia! O preco da raquete <strong>{paddle_name}</strong>
      baixou para o seu preco alvo.
    </p>
    <ul>
      <li>Preco atual: <strong>R$ {current_price:.2f}</strong></li>
      <li>Seu preco alvo: R$ {price_target:.2f}</li>
    </ul>
    <p>Aproveite enquanto dura!</p>
    <hr>
    <small>Para cancelar alertas acesse sua conta em pickleiq.com.</small>
  </body>
</html>
""".strip()


async def send_email(
    client: httpx.AsyncClient,
    to_email: str,
    paddle_name: str,
    current_price: float,
    price_target: float,
) -> bool:
    """Send price alert email via Resend. Returns True on success."""
    payload = {
        "from": FROM_EMAIL,
        "to": to_email,
        "subject": f"Raquete em promocao! R$ {current_price:.2f}",
        "html": _build_alert_email_html(paddle_name, current_price, price_target),
        "headers": {
            "List-Unsubscribe": f"<mailto:unsubscribe@pickleiq.com>",
        },
    }
    try:
        res = await client.post(
            RESEND_ENDPOINT,
            headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
            json=payload,
            timeout=10.0,
        )
        if res.status_code in (200, 201):
            return True
        logger.error("Resend API error %s: %s", res.status_code, res.text)
        return False
    except httpx.RequestError as exc:
        logger.error("Resend HTTP request failed: %s", exc)
        return False


async def check_price_alerts() -> tuple[int, int]:
    """Main worker logic. Returns (checked_count, triggered_count)."""
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL env var is required")
    if not RESEND_API_KEY:
        raise RuntimeError("RESEND_API_KEY env var is required")

    now = datetime.now(timezone.utc)
    cooldown_cutoff = now - timedelta(hours=COOLDOWN_HOURS)

    checked_count = 0
    triggered_count = 0

    async with await psycopg.AsyncConnection.connect(DATABASE_URL) as conn:
        # Fetch active alerts not triggered in the last 24h (idempotent guard)
        rows = await conn.execute(
            """
            SELECT
                pa.id,
                pa.user_id,
                pa.paddle_id,
                pa.price_target,
                pa.last_triggered,
                p.name AS paddle_name,
                u.email
            FROM price_alerts pa
            JOIN paddles p ON p.id = pa.paddle_id
            JOIN users u ON u.id = pa.user_id
            WHERE pa.active = true
              AND (pa.last_triggered IS NULL OR pa.last_triggered < %s)
            """,
            (cooldown_cutoff,),
        )
        alerts = await rows.fetchall()

        logger.info("Found %d eligible alert(s) to check.", len(alerts))

        async with httpx.AsyncClient() as client:
            for row in alerts:
                (
                    alert_id,
                    user_id,
                    paddle_id,
                    price_target,
                    last_triggered,
                    paddle_name,
                    email,
                ) = row
                checked_count += 1

                # Fetch lowest current price across all retailers
                price_row = await conn.execute(
                    """
                    SELECT MIN(price_brl) AS current_price
                    FROM latest_prices
                    WHERE paddle_id = %s
                    """,
                    (paddle_id,),
                )
                price_result = await price_row.fetchone()
                current_price = price_result[0] if price_result else None

                if current_price is None:
                    logger.info(
                        "[SKIP] Alert %s: no price data for paddle %s",
                        alert_id,
                        paddle_id,
                    )
                    continue

                current_price = float(current_price)
                price_target_f = float(price_target)

                if current_price <= price_target_f:
                    sent = await send_email(
                        client, email, paddle_name, current_price, price_target_f
                    )
                    if sent:
                        await conn.execute(
                            "UPDATE price_alerts SET last_triggered = %s WHERE id = %s",
                            (now, alert_id),
                        )
                        await conn.commit()
                        triggered_count += 1
                        logger.info(
                            "[OK] Alert %s: email sent to %s (R$ %.2f <= R$ %.2f)",
                            alert_id,
                            email,
                            current_price,
                            price_target_f,
                        )
                    else:
                        logger.warning("[FAIL] Alert %s: email send failed", alert_id)
                else:
                    logger.debug(
                        "[SKIP] Alert %s: price R$ %.2f > target R$ %.2f",
                        alert_id,
                        current_price,
                        price_target_f,
                    )

    return checked_count, triggered_count


async def main() -> None:
    checked, triggered = await check_price_alerts()
    logger.info("Checked %d alerts, triggered %d emails.", checked, triggered)


if __name__ == "__main__":
    asyncio.run(main())
