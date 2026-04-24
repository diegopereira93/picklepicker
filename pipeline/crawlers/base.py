"""Base crawler class with shared retry/dedup/insert logic.

All crawlers inherit from BaseCrawler and implement:
  - fetch_products(): fetch raw product data from retailer
  - parse_product(): convert a single raw item to standardized format (optional)

The base class handles:
  - DB connection lifecycle (get_connection, commit, refresh materialized view)
  - Dedup pipeline (tier2_match → fuzzy_match → upsert paddles)
  - Paddle specs upsert
  - Price snapshot insertion
  - Telegram alerting on failure
  - Structured logging
"""

import json
import logging
from abc import ABC, abstractmethod

from pipeline.alerts.telegram import send_telegram_alert
from pipeline.crawlers.utils import extract_brand_from_name, normalize_paddle_name
from pipeline.crawlers.validation import validate_product
from pipeline.db.connection import get_connection
from pipeline.dedup.normalizer import tier2_match, title_hash
from pipeline.dedup.spec_matcher import fuzzy_match_paddles

logger = logging.getLogger(__name__)


class BaseCrawler(ABC):
    """Abstract base class for pickleball paddle crawlers.

    Subclasses must set:
      - retailer_id: int  (matches retailers table)
      - retailer_name: str  (human-readable, used in logs/alerts)

    Subclasses must implement:
      - fetch_products(): fetch raw data from retailer
    """

    retailer_id: int
    retailer_name: str

    @abstractmethod
    async def fetch_products(self) -> list[dict]:
        """Fetch raw product data from the retailer.

        Returns a list of product dicts, each with at least:
          name, brand, price_brl, image_url, product_url, in_stock, specs
        """
        ...

    async def run(self) -> int:
        """Main entry point: fetch, validate, dedup, save products to DB.

        Returns count of saved price snapshots.
        Sends Telegram alert on fetch failure.
        """
        try:
            products = await self.fetch_products()
        except Exception as e:
            error_msg = str(e)
            logger.error("%s crawler failed: %s", self.retailer_name, error_msg)
            await send_telegram_alert(
                f"{self.retailer_name} crawler failed: {error_msg}"
            )
            raise

        logger.info(
            "Extracted %d products from %s", len(products), self.retailer_name
        )

        if not products:
            logger.warning("No products extracted from %s", self.retailer_name)
            return 0

        async with get_connection() as conn:
            saved = await self.save_products_to_db(products, conn)
            await conn.execute("REFRESH MATERIALIZED VIEW CONCURRENTLY latest_prices")
            await conn.commit()

        logger.info("Saved %d products to price_snapshots", saved)
        return saved

    async def save_products_to_db(
        self, products: list[dict], conn
    ) -> int:
        """Save parsed products to paddles + price_snapshots + paddle_specs.

        Uses atomic upsert for paddles (INSERT ... ON CONFLICT DO UPDATE)
        with dedup pipeline: tier2_match → fuzzy_match → review_queue logging.

        Validates products before insertion. Skips invalid with warning log.
        Returns count of saved price snapshots.
        """
        saved = 0
        for product in products:
            # Validate product data
            is_valid, errors = validate_product(product)
            if not is_valid:
                logger.warning(
                    "Skipping invalid product %s: %s",
                    product.get("name", "unknown"),
                    "; ".join(errors),
                )
                continue

            price = product.get("price_brl")
            if price is None:
                logger.warning(
                    "Skipping product %s: missing price_brl",
                    product.get("name", "unknown"),
                )
                continue

            raw_name = product.get("name", "")
            name = normalize_paddle_name(raw_name)
            raw_brand = product.get("brand", "")
            brand = raw_brand if raw_brand else extract_brand_from_name(raw_name)
            image_url = product.get("image_url", "")

            # --- Dedup pipeline ---
            existing_id = await tier2_match(raw_name)
            if existing_id is not None:
                paddle_id = existing_id
                logger.info(
                    "Dedup tier-2 match for '%s': reusing paddle_id=%d",
                    name,
                    paddle_id,
                )
            else:
                fuzzy_id, fuzzy_score = await fuzzy_match_paddles(
                    raw_name, threshold=0.85
                )

                hash_value = title_hash(raw_name)
                result = await conn.execute(
                    """
                    INSERT INTO paddles (name, brand, model, image_url, in_stock, price_min_brl, title_hash)
                    VALUES (%(name)s, %(brand)s, %(model)s, %(image_url)s, %(in_stock)s, %(price_min_brl)s, %(title_hash)s)
                    ON CONFLICT (name) DO UPDATE SET
                        brand = EXCLUDED.brand,
                        model = EXCLUDED.model,
                        image_url = COALESCE(NULLIF(EXCLUDED.image_url, ''), paddles.image_url),
                        in_stock = EXCLUDED.in_stock,
                        price_min_brl = LEAST(paddles.price_min_brl, EXCLUDED.price_min_brl),
                        title_hash = EXCLUDED.title_hash,
                        updated_at = NOW()
                    RETURNING id
                    """,
                    {
                        "name": name,
                        "brand": brand or "",
                        "model": name,
                        "image_url": image_url,
                        "in_stock": product.get("in_stock", True),
                        "price_min_brl": price,
                        "title_hash": hash_value,
                    },
                )
                row = await result.fetchone()
                if row is None:
                    logger.error("Upsert failed for paddle: %s", name)
                    continue

                paddle_id = row[0]

                # Log potential duplicate to review_queue (conservative: still saved)
                if fuzzy_id is not None:
                    logger.warning(
                        "Dedup fuzzy match for '%s': similar to paddle_id=%d (score=%.3f) — logged to review_queue",
                        name,
                        fuzzy_id,
                        fuzzy_score,
                    )
                    await conn.execute(
                        """
                        INSERT INTO review_queue (type, paddle_id, related_paddle_id, data, status)
                        VALUES ('duplicate', %(paddle_id)s, %(related_id)s, %(data)s, 'pending')
                        """,
                        {
                            "paddle_id": fuzzy_id,
                            "related_id": paddle_id,
                            "data": json.dumps(
                                {"raw_name": raw_name, "score": fuzzy_score}
                            ),
                        },
                    )

                # Upsert paddle_specs if any specs present
                self._upsert_specs(conn, paddle_id, product.get("specs", {}))

            # Always record price snapshot (for both tier-2 matches and new paddles)
            await conn.execute(
                """
                INSERT INTO price_snapshots
                    (paddle_id, retailer_id, price_brl, currency, in_stock, affiliate_url, scraped_at, source_raw)
                VALUES
                    (%(paddle_id)s, %(retailer_id)s, %(price_brl)s, 'BRL', %(in_stock)s, %(affiliate_url)s, NOW(), %(source_raw)s)
                """,
                {
                    "paddle_id": paddle_id,
                    "retailer_id": self.retailer_id,
                    "price_brl": price,
                    "in_stock": product.get("in_stock", True),
                    "affiliate_url": product.get("product_url", ""),
                    "source_raw": json.dumps(product),
                },
            )
            saved += 1

        return saved

    @staticmethod
    async def _upsert_specs(conn, paddle_id: int, specs: dict) -> None:
        """Upsert paddle_specs for a paddle. No-op if specs dict is empty."""
        if not specs or not any(specs.values()):
            return

        spec_fields: dict = {}
        if specs.get("weight_oz") is not None:
            spec_fields["weight_oz"] = specs["weight_oz"]
        if specs.get("face_material"):
            spec_fields["face_material"] = specs["face_material"]
        if specs.get("core_thickness_mm") is not None:
            spec_fields["core_thickness_mm"] = specs["core_thickness_mm"]
        if specs.get("grip_size"):
            spec_fields["grip_size"] = specs["grip_size"]

        if not spec_fields:
            return

        columns = list(spec_fields.keys())
        set_clauses = ", ".join(f"{col} = EXCLUDED.{col}" for col in columns)

        await conn.execute(
            f"""
            INSERT INTO paddle_specs (paddle_id, {', '.join(columns)})
            VALUES (%(paddle_id)s, {', '.join(f'%({c})s' for c in columns)})
            ON CONFLICT (paddle_id) DO UPDATE SET
                {set_clauses}, updated_at = NOW()
            """,
            {"paddle_id": paddle_id, **spec_fields},
        )
