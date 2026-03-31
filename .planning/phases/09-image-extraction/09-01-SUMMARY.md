---
phase: "09-image-extraction"
plan: "01"
subsystem: "crawler"
tags: ["brazil-store", "image-extraction", "firecrawl", "crawler"]
dependency_graph:
  requires: []
  provides: ["IMG-01", "IMG-02", "IMG-03", "IMG-04", "IMG-05"]
  affects: ["brazil_store_crawler", "catalog_images"]
tech-stack:
  added: ["firecrawl.scrape", "tenacity.retry"]
  patterns: ["two-phase-extraction", "rate-limiting", "url-transformation"]
key-files:
  created:
    - pipeline/test_image_extraction.py
  modified:
    - pipeline/crawlers/brazil_store.py
decisions:
  - Use Firecrawl scrape() instead of extract() for product pages to get full markdown
  - Transform mitiendanube URLs from -1024-1024 to -480-0 for optimized size
  - Add 1-second delay between product page scrapes to avoid rate limiting
  - Filter for mitiendanube.com CDN URLs specifically for Brazil Store
metrics:
  duration: "15min"
  completed_date: "2026-03-31"
  tasks: 4
  files: 2
---

# Phase 09 Plan 01: Brazil Store Two-Phase Image Extraction Summary

**One-liner:** Enhanced Brazil Store crawler to extract real product images from individual product pages using two-phase extraction (category page + product pages).

## What Was Built

### Problem
Only 2/34 paddles (6%) had real images from Brazil Pickleball Store. The Firecrawl `extract()` method on category pages doesn't capture lazy-loaded images that only appear when viewing individual product pages.

### Solution
Implemented two-phase extraction:
1. **Phase 1:** Extract product list from category page (existing)
2. **Phase 2:** Scrape individual product pages to extract real image URLs from markdown

### Implementation

#### New Functions Added

1. **`extract_image_from_markdown(markdown: str) -> Optional[str]`**
   - Extracts image URLs from markdown content using regex pattern
   - Filters for mitiendanube.com CDN URLs
   - Transforms URLs: `-1024-1024` → `-480-0` for smaller optimized size

2. **`scrape_product_page(app: FirecrawlApp, url: str) -> Optional[str]`**
   - Scrapes individual product page using Firecrawl `scrape()` method
   - Includes `@retry` decorator with exponential backoff (3 attempts, 5-60s wait)
   - Returns extracted image URL or None

#### Modified Functions

3. **`run_brazil_store_crawler()`**
   - Added Phase 2 loop to enhance products with images
   - Rate limiting: 1-second delay between product page scrapes
   - Only scrapes products with missing/placeholder images
   - Logs progress: "Phase 2 complete: X/Y products have images"

#### Test Script

4. **`pipeline/test_image_extraction.py`**
   - Tests markdown extraction with sample data
   - Validates URL transformation logic
   - Optional live crawler test (requires API key)

## Tasks Completed

| # | Task | Status | Commit |
|---|------|--------|--------|
| 1 | Add extract_image_from_markdown() helper | ✅ | ffc90d2 |
| 2 | Create scrape_product_page() function | ✅ | ffc90d2 |
| 3 | Modify run_brazil_store_crawler for two-phase extraction | ✅ | ffc90d2 |
| 4 | Create test script for validation | ✅ | ffc90d2 |

## Verification Results

### Unit Tests (No API Key Required)
```
✓ Test 1 - mitiendanube: https://dcdn.mitiendanube.com/.../raquete-480-0.jpg
✓ Test 2 - non-mitiendanube: None
✓ Test 3 - empty: None
```

### Code Verification
```bash
$ grep -n "def extract_image_from_markdown" pipeline/crawlers/brazil_store.py
56:def extract_image_from_markdown(markdown: str) -> Optional[str]:

$ grep -n "def scrape_product_page" pipeline/crawlers/brazil_store.py
75:def scrape_product_page(app: FirecrawlApp, url: str) -> Optional[str]:

$ grep -n "Phase 2" pipeline/crawlers/brazil_store.py
153:    # Phase 2: Scrape individual product pages for images
154:    logger.info("Starting Phase 2: Scraping individual product pages for images...")
172:    logger.info(f"Phase 2 complete: {len(products_with_images)}/{len(products)} products have images")
```

## Key Technical Details

### Image URL Transformation
- Input: `https://dcdn.mitiendanube.com/.../image-1024-1024.jpg`
- Output: `https://dcdn.mitiendanube.com/.../image-480-0.jpg`
- Reduces image size from ~1024px to 480px width

### Rate Limiting
- 1-second delay between individual product page scrapes
- Prevents Firecrawl API rate limiting
- Only applies to products needing image extraction

### Retry Logic
- 3 attempts with exponential backoff
- Wait: 5s → 10s → 20s (max 60s)
- Reraises exception after all retries exhausted

## Success Criteria Checklist

- [x] Brazil Store crawler has extract_image_from_markdown() helper
- [x] FIRECRAWL_SCHEMA already included image_url field (was already present)
- [x] Two-phase extraction implemented (category + product pages)
- [x] Test script validates implementation
- [x] Image URLs are filtered for mitiendanube.com CDN

## Deviations from Plan

None - plan executed exactly as written.

## Next Steps

To fully validate the implementation with live data:

1. Set `FIRECRAWL_API_KEY` environment variable
2. Run: `cd pipeline && python3 test_image_extraction.py`
3. When prompted, enter `y` to run crawler test
4. Expected: 50%+ of products should have real image URLs

## Commits

- `ffc90d2`: feat(09-01): enhance Brazil Store crawler with two-phase image extraction

## Files Modified

- `pipeline/crawlers/brazil_store.py` - Added helper functions and two-phase extraction
- `pipeline/test_image_extraction.py` - Created test script (new file)
