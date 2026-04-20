"""Data validation for scraped paddle products."""

import re
from typing import Any


def validate_product(product: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a scraped product dict before DB insertion.

    Returns (is_valid, list_of_error_reasons).
    """
    errors: list[str] = []

    name = product.get("name", "")
    if not name or not isinstance(name, str):
        errors.append("name is missing or not a string")
    elif len(name.strip()) <= 5:
        errors.append(f"name too short ({len(name.strip())} chars, need >5): '{name[:30]}'")

    price = product.get("price_brl")
    if price is None:
        errors.append("price_brl is missing")
    elif not isinstance(price, (int, float)):
        errors.append(f"price_brl is not a number: {price!r}")
    elif price <= 0:
        errors.append(f"price_brl must be > 0: {price}")
    elif price >= 50000:
        errors.append(f"price_brl suspiciously high (>=50000): {price}")

    product_url = product.get("product_url")
    if product_url and not isinstance(product_url, str):
        errors.append(f"product_url is not a string: {product_url!r}")
    elif product_url and not _is_http_url(product_url):
        errors.append(f"product_url is not a valid HTTP URL: '{product_url[:60]}'")

    image_url = product.get("image_url", "")
    if image_url and not _is_http_url(image_url):
        errors.append(f"image_url is not a valid HTTP URL: '{image_url[:60]}'")

    return (len(errors) == 0, errors)


_URL_RE = re.compile(r"^https?://\S+$", re.IGNORECASE)


def _is_http_url(value: str) -> bool:
    return bool(_URL_RE.match(value))
