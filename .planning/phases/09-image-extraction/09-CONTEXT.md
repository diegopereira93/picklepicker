---
phase: 09-image-extraction
status: planning
type: gap_closure
created: 2026-03-31
---

# Phase 09: Real Product Image Extraction

## Goal
Fix catalog to display real product images from retailers instead of generic placeholders. Currently only 2/34 paddles (6%) have real images.

## Problem
- 2 paddles: Real images from Brazil Pickleball Store
- 32 paddles: Generic Unsplash placeholders
- Root cause: Firecrawl extract() doesn't capture lazy-loaded images from category pages

## Solution
Enhance Brazil Store crawler with two-phase extraction:
1. Extract product list from category page
2. Scrape individual product pages to get real image URLs

## Requirements
- IMG-01: Scrape product pages for real image URLs
- IMG-02: Update brazil_store.py crawler with two-phase extraction
- IMG-03: Add image extraction helper and schema updates
- IMG-04: Test on 10+ products to validate
- IMG-05: Fallback to placeholder if extraction fails

## Success Criteria
- 80% of paddles have real product images (not placeholders)
- Images load successfully in catalog page
- Image extraction runs as part of daily scraper job

## Source Gap
.planning/gaps/09-image-extraction-gap.md
