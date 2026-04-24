import os
import logging
import re
import time
from typing import Optional
from firecrawl import FirecrawlApp
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from pipeline.crawlers.base import BaseCrawler
from pipeline.crawlers.utils import extract_brand_from_name, normalize_paddle_name, validate_image_belongs_to_product
from pipeline.dedup.normalizer import tier2_match, title_hash
from pipeline.dedup.spec_matcher import fuzzy_match_paddles

logger = logging.getLogger(__name__)

BRAZIL_STORE_URL = "https://www.brazilpickleballstore.com.br/raquete/"

FIRECRAWL_SCHEMA = {
    "type": "object",
    "properties": {
        "products": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "price_brl": {"type": "number"},
                    "in_stock": {"type": "boolean"},
                    "image_url": {"type": "string"},
                    "product_url": {"type": "string"},
                    "brand": {"type": "string"},
                    "specs": {
                        "type": "object",
                        "properties": {
                            "weight_oz": {"type": "number"},
                            "face_material": {"type": "string"},
                            "core_material": {"type": "string"},
                            "core_thickness_mm": {"type": "number"},
                            "grip_size": {"type": "string"},
                        },
                    },
                },
            },
        }
    },
}

GRAMS_TO_OZ = 1 / 28.3495

FACE_MATERIAL_MAP = {
    "carbono": "Carbon Fiber",
    "carbon": "Carbon Fiber",
    "fibra de carbono": "Carbon Fiber",
    "carbon fiber": "Carbon Fiber",
    "fibra de vidro": "Fiberglass",
    "fiberglass": "Fiberglass",
    "glass fiber": "Fiberglass",
    "grafite": "Graphite",
    "graphite": "Graphite",
    "kevlar": "Kevlar",
    "hybrid": "Hybrid",
    "t700": "T700 Carbon Fiber",
}


def extract_specs_from_markdown(markdown: str) -> dict:
    """Parse PT-BR spec patterns from product page markdown.

    Recognizes patterns like:
      Peso: 230g / 8.1 oz
      Face: Carbono / Fiberglass / Graphite
      Núcleo: PP / Polymer / Polipropileno
      Espessura: 16mm
      Cabo / Grip: 4.25"
    """
    specs: dict = {}
    text = markdown.lower()

    weight_match = re.search(r"peso[:\s]+(\d+(?:[.,]\d+)?)\s*g", text)
    if weight_match:
        grams = float(weight_match.group(1).replace(",", "."))
        specs["weight_oz"] = round(grams * GRAMS_TO_OZ, 2)
    else:
        oz_match = re.search(r"(\d+(?:[.,]\d+)?)\s*oz", text)
        if oz_match:
            specs["weight_oz"] = float(oz_match.group(1).replace(",", "."))

    face_match = re.search(
        r"(?:face|superf[ií]cie|material\s+da\s+face)[:\s]+([a-zà-úa-z\s]+?)(?:\n|,|\.|$)",
        text,
    )
    if face_match:
        raw_face = face_match.group(1).strip()
        for pt_key, en_val in FACE_MATERIAL_MAP.items():
            if pt_key in raw_face:
                specs["face_material"] = en_val
                break

    thickness_match = re.search(r"espessura[:\s]+(\d+(?:[.,]\d+)?)\s*mm", text)
    if thickness_match:
        specs["core_thickness_mm"] = float(thickness_match.group(1).replace(",", "."))

    grip_match = re.search(r"(?:cabo|grip|punho)[:\s]+([\d\s/]+(?:\"|'))", text)
    if grip_match:
        specs["grip_size"] = grip_match.group(1).strip().rstrip("\"'").strip()

    return specs


def _try_structured_extraction(app: FirecrawlApp, url: str) -> list[dict]:
    try:
        result = app.scrape(
            url,
            formats=[{
                "type": "json",
                "prompt": (
                    "Extract all pickleball paddle products from this page. "
                    "For each product include: name, price_brl (as number), "
                    "in_stock (boolean), image_url, product_url, brand, and specs "
                    "(weight_oz, face_material, core_material, core_thickness_mm, grip_size)."
                ),
                "schema": FIRECRAWL_SCHEMA,
            }],
        )
        products = []
        if hasattr(result, "json") and result.json:
            data = result.json
        elif hasattr(result, "extract") and result.extract:
            data = result.extract
        elif isinstance(result, dict):
            data = result.get("json") or result.get("extract") or {}
        else:
            return []

        extracted = data.get("products", []) if isinstance(data, dict) else []
        for item in extracted:
            if not isinstance(item, dict) or not item.get("name"):
                continue
            product = {
                "name": item.get("name", ""),
                "price_brl": item.get("price_brl"),
                "in_stock": item.get("in_stock", True),
                "image_url": item.get("image_url", ""),
                "product_url": item.get("product_url", ""),
                "url": item.get("product_url", ""),
                "brand": item.get("brand", ""),
                "specs": item.get("specs", {}),
            }
            if product["price_brl"] is not None:
                try:
                    product["price_brl"] = float(product["price_brl"])
                except (ValueError, TypeError):
                    product["price_brl"] = None
            products.append(product)

        logger.info("Structured extraction returned %d products", len(products))
        return products
    except Exception as e:
        logger.warning("Structured extraction failed, will use markdown fallback: %s", e)
        return []


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=10, max=120),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def extract_products(app: FirecrawlApp, url: str) -> dict:
    structured = _try_structured_extraction(app, url)
    if len(structured) >= 3:
        return {"data": {"products": structured}}

    logger.info(
        "Structured extraction returned %d products (< 3 threshold), using markdown parsing",
        len(structured),
    )

    result = app.scrape(url)

    if hasattr(result, 'markdown'):
        markdown = result.markdown
    elif isinstance(result, dict):
        markdown = result.get('markdown', '')
    else:
        markdown = str(result)

    lines = markdown.split('\n')
    products = []

    i = 0
    while i < len(lines):
        line = lines[i]

        if line.startswith('[Raquete'):
            name = line[9:].rstrip('\\').strip()
            full_name = 'Raquete ' + name

            price = None
            for j in range(i+1, min(i+20, len(lines))):
                if lines[j].startswith('R$') and '\\\\n\\\\n' not in lines[j]:
                    price_match = re.search(r'R\$([\d\.,]+)', lines[j])
                    if price_match:
                        price_str = price_match.group(1)
                        price = float(price_str.replace('.', '').replace(',', '.'))
                        break

            product_url = ''
            for j in range(max(0, i-10), i):
                prev_line = lines[j]
                if 'brazilpickleballstore.com.br/produtos/' in prev_line:
                    url_match = re.search(r'\]\((https?://[^\)]+)\s*"', prev_line)
                    if url_match:
                        product_url = url_match.group(1).rstrip('"')
                        break
                    url_match2 = re.search(r'https?://[^\s\)]+produtos[^\s\)]+', prev_line)
                    if url_match2:
                        product_url = url_match2.group(0)
                        break

            if price:
                products.append({
                    "name": full_name,
                    "price_brl": price,
                    "product_url": product_url,
                    "url": product_url,
                    "image_url": "",
                    "brand": extract_brand_from_name(full_name),
                    "in_stock": True,
                    "specs": {},
                })

        i += 1

    logger.info("Parsed %d products from markdown", len(products))

    return {"data": {"products": products}}


def extract_image_from_markdown(markdown: str) -> Optional[str]:
    pattern = r'!\[.*?\]\((https?://[^)]+\.(?:jpg|jpeg|png|webp))\)'
    matches = re.findall(pattern, markdown, re.IGNORECASE)
    
    if not matches:
        return None
    
    for match in matches:
        if 'mitiendanube.com' in match:
            return match.replace('-1024-1024', '-480-0')
    
    for match in matches:
        if 'cloudfront.net' in match:
            return match
    
    for match in matches:
        if 'amazonaws.com' in match:
            return match
    
    for match in matches:
        if 'cdn' in match:
            return match
    
    for match in matches:
        if len(match) > 80:
            return match
    
    return matches[0] if matches else None


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=5, max=60),
    retry=retry_if_exception_type(Exception),
    reraise=True,
)
def scrape_product_page(app: FirecrawlApp, product_url: str) -> Optional[tuple[str, dict]]:
    try:
        result = app.scrape(product_url)
        if hasattr(result, 'markdown'):
            markdown = result.markdown
        elif isinstance(result, dict):
            markdown = result.get('markdown', '')
        else:
            return None

        image_url = extract_image_from_markdown(markdown)
        specs = extract_specs_from_markdown(markdown)
        return (image_url, specs)
    except Exception as e:
        logger.warning("Failed to scrape product page %s: %s", product_url, e)
        return None


class BrazilStoreCrawler(BaseCrawler):
    retailer_id = 1
    retailer_name = "Brazil Pickleball Store"

    def __init__(self, app: FirecrawlApp | None = None):
        self.app = app

    async def fetch_products(self) -> list[dict]:
        app = self.app
        if app is None:
            app = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])

        result = extract_products(app, BRAZIL_STORE_URL)

        if hasattr(result, 'model_dump'):
            result = result.model_dump()
        elif hasattr(result, 'dict'):
            result = result.dict()

        products = (result.get("data") or {}).get("products", [])

        logger.info("Starting Phase 2: Scraping individual product pages for images and specs...")
        for i, product in enumerate(products):
            product_url = product.get("product_url") or product.get("url")
            current_image = product.get("image_url", "")
            product_name = product.get("name", "Unknown")

            if product_url:
                logger.debug(f"Scraping product page {i+1}/{len(products)}: {product_url}")
                phase2_result = scrape_product_page(app, product_url)
                if phase2_result:
                    phase2_image, phase2_specs = phase2_result

                    if phase2_specs and any(phase2_specs.values()):
                        existing_specs = product.get("specs", {})
                        merged = {**existing_specs, **{k: v for k, v in phase2_specs.items() if v}}
                        product["specs"] = merged

                    if phase2_image:
                        should_replace = False
                        if not current_image:
                            should_replace = True
                        elif "placeholder" in current_image.lower():
                            should_replace = True
                        elif len(phase2_image) > len(current_image) + 20:
                            should_replace = True
                        elif current_image.count("/") < phase2_image.count("/"):
                            should_replace = True
                        
                        if should_replace and not validate_image_belongs_to_product(phase2_image, product_name):
                            logger.warning(f"Phase 2 image for '{product_name[:40]}' may not belong to product: {phase2_image[:60]}...")
                            if not current_image or "placeholder" in current_image.lower():
                                pass
                            else:
                                should_replace = False

                        if should_replace:
                            product["image_url"] = phase2_image
                            logger.info(f"Phase 2 image for '{product_name[:40]}...': {phase2_image[:60]}...")
            
                if i < len(products) - 1:
                    time.sleep(1)

        products_with_images = [p for p in products if p.get("image_url")]
        products_with_specs = [p for p in products if p.get("specs") and any(p["specs"].values())]
        logger.info(
            f"Phase 2 complete: {len(products_with_images)}/{len(products)} images, "
            f"{len(products_with_specs)}/{len(products)} with specs"
        )

        return products


async def run_brazil_store_crawler(app: FirecrawlApp | None = None) -> int:
    return await BrazilStoreCrawler(app=app).run()


if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(run_brazil_store_crawler())
