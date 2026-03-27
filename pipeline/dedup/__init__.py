"""Deduplication module for PickleIQ.

Implements 3-tier deduplication strategy:
1. Tier 1: Manufacturer SKU exact match
2. Tier 2: Title normalization + hash-based matching
3. Tier 3: RapidFuzz fuzzy matching with threshold ≥ 0.85
"""
