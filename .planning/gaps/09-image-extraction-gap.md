# Gap 09: Real Product Image Extraction

## Status
**Identified:** 2026-03-31
**Priority:** High
**Category:** Data Pipeline / Scraper Enhancement

## Problem Statement

The catalog currently displays:
- **2 paddles** with real images from Brazil Pickleball Store (mitiendanube.com CDN)
- **32 paddles** with generic Unsplash placeholder images
- **0 paddles** with manufacturer/retailer direct product images

This degrades the user experience and doesn't fulfill the product promise of showing real pickleball paddles.

## Root Cause

1. **Scraper limitation**: The Firecrawl extract() endpoint returns empty `image_url` fields for products on category pages
2. **Lazy loading**: Brazil Pickleball Store uses lazy-loaded images that require JavaScript execution
3. **No image persistence**: Previous scraper runs only captured placeholder URLs (`example.com`)
4. **Missing product page scraping**: Current pipeline scrapes category pages but not individual product pages where images are fully loaded

## Evidence

### Current Database State
```sql
SELECT
    CASE
        WHEN image_url LIKE '%mitiendanube%' THEN 'REAL (Scraper)'
        WHEN image_url LIKE '%unsplash%' THEN 'Generic (Placeholder)'
        ELSE 'Other'
    END as image_source,
    COUNT(*) as count
FROM paddles
GROUP BY image_source;

-- Result:
-- REAL (Scraper)     | 2
-- Generic (Placeholder) | 32
```

### Successfully Extracted Real Images
| Brand | Product | Image URL |
|-------|---------|-----------|
| Selkirk | Invikta Luxx Control | `https://acdn-us.mitiendanube.com/stores/002/859/813/products/4-870cf1d41c2fd235ce17611432160834-480-0.webp` |
| Paddletek | Tempest Reign V3 | `https://acdn-us.mitiendanube.com/stores/002/859/813/products/1111-bf35cad65f7287698b16920175228705-480-0.webp` |
| ProXR | Signature Series | `https://acdn-us.mitiendanube.com/stores/002/859/813/products/29-8a5ead0bbf4111b55317234848049217-480-0.webp` |

## Proposed Solutions

### Option A: Enhanced Product Page Scraping (Recommended)
- Modify crawler to visit individual product pages after category extraction
- Use Firecrawl `scrape()` method which captures lazy-loaded images
- Extract first product image from markdown: `!\[.*?\]\((https?://[^)]+)\)`
- Update `brazil_store.py` crawler with two-phase extraction:
  1. Extract product list from category page
  2. For each product, scrape product page to get real image URL

### Option B: Image CDN Integration
- Integrate with Brazil Pickleball Store's CDN (mitiendanube.com)
- Construct image URLs from product SKUs if pattern is consistent
- Store base CDN path and construct URLs dynamically

### Option C: Manufacturer API Integration
- Contact manufacturers (Selkirk, JOOLA, Paddletek, etc.) for official product images
- Create image synchronization pipeline
- Host images in project's own CDN (Supabase Storage or similar)

## Implementation Plan

### Phase 1: Fix Brazil Store Crawler
- [ ] Modify `pipeline/crawlers/brazil_store.py` to scrape product pages
- [ ] Add `extract_image_from_markdown()` helper function
- [ ] Update `FIRECRAWL_SCHEMA` to capture image URLs from product pages
- [ ] Test extraction on 10+ product pages

### Phase 2: Image Deduplication
- [ ] Create `paddle_images` table to store multiple images per paddle
- [ ] Implement image similarity check (perceptual hashing)
- [ ] Handle case where same product has different images across retailers

### Phase 3: Image Fallback Strategy
- [ ] Define hierarchy: retailer real image > manufacturer image > generic placeholder
- [ ] Add `image_source` column to track image provenance
- [ ] Create image refresh job to update stale images

## Technical Notes

### Working Image Extraction Pattern
```python
from firecrawl import FirecrawlApp
import re

app = FirecrawlApp(api_key=os.environ["FIRECRAWL_API_KEY"])
result = app.scrape("https://brazilpickleballstore.com.br/produto/{product-slug}")

# Extract from markdown
pattern = r'!\[.*?\]\((https?://[^)]+\.(?:jpg|jpeg|png|webp))\)'
matches = re.findall(pattern, result.markdown, re.IGNORECASE)

# Filter for CDN images
for match in matches:
    if 'mitiendanube.com' in match:
        image_url = match.replace('-1024-1024', '-480-0')
```

### Affected Files
- `pipeline/crawlers/brazil_store.py` - Main crawler enhancement
- `pipeline/crawlers/dropshot_brasil.py` - Apply same pattern
- `pipeline/db/schema.sql` - May need `paddle_images` table
- `backend/app/schemas.py` - Update to support multiple images

## Success Criteria

- [ ] 80% of paddles have real product images (not placeholders)
- [ ] Images load successfully in catalog page (`<img src>` returns 200)
- [ ] Image extraction runs as part of daily scraper job
- [ ] Fallback to placeholder if real image fails to load

## Related

- Phase 08-04: Database population with enriched data (completed)
- Phase 07: E2E testing infrastructure (has Firecrawl integration patterns)
- `scripts/extract_real_images.py` - Script started but not completed

## Dependencies

- Requires Firecrawl API key (already configured)
- Requires Brazil Pickleball Store website accessibility
- May need rate limiting to avoid blocking

---

**Next Action:** Schedule as Phase 09 in roadmap
**Estimated Effort:** 1-2 days
**Impact:** High UX improvement
