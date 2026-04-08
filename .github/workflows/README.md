# GitHub Actions Workflows

This directory contains all GitHub Actions workflows for the PickleIQ project.

## Workflows Overview

| Workflow | Trigger | Purpose | Status |
|----------|---------|---------|--------|
| **deploy.yml** | PR to main, push to main | Test, deploy preview (PR), deploy production (main) | ✅ Active |
| **lighthouse.yml** | PR to main, manual | Lighthouse CI performance audit | ✅ Active |
| **nps-survey.yml** | Daily at 9 AM UTC | Send NPS surveys to users (30+ days) | ✅ Active |
| **price-alerts-check.yml** | Daily at 6 AM UTC | Check and send price alerts | ✅ Active |
| **scraper.yml** | Daily at 2:00/2:05/2:10 UTC | Run all data crawlers | ✅ Active |
| **test.yml** | PR to main/develop, push to main | Run tests with coverage | ✅ Active |
| **validate-production.yml** | Daily at 12 PM UTC, manual | Production validation with Playwright | ✅ Active |

## Changes Made (Workflow Cleanup)

### Removed
- ~~`scrape.yml`~~ - Removed (duplicated scraper.yml functionality and referenced non-existent crawlers)

### Fixed
1. **Python Version Consistency**: Updated all workflows from Python 3.11 → 3.12
   - `deploy.yml`
   - `scraper.yml`
   - `test.yml`
   - `price-alerts-check.yml`
   - `nps-survey.yml`

2. **YAML Syntax**: Fixed indentation issues in `scraper.yml`

3. **Lighthouse Triggers**: Changed from `on: [push]` to only run on PRs

## Scheduled Workflow Times (UTC)

| Time | Workflow | BRT (UTC-3) |
|------|----------|-------------|
| 02:00/02:05/02:10 | scraper.yml | 23:00/23:05/23:10 |
| 06:00 | price-alerts-check.yml | 03:00 |
| 09:00 | nps-survey.yml | 06:00 |
| 12:00 | validate-production.yml | 09:00 |

## Secrets Required

All workflows expect these secrets to be configured in the repository:

- `DATABASE_URL` - PostgreSQL connection string
- `FIRECRAWL_API_KEY` - Firecrawl API key for scraping
- `MERCADO_LIVRE_API_KEY` - Mercado Livre API key
- `TELEGRAM_BOT_TOKEN` - Telegram bot for alerts
- `TELEGRAM_CHAT_ID` - Telegram chat ID for alerts
- `VERCEL_TOKEN` - Vercel deployment token
- `VERCEL_PROJECT_ID` - Vercel project ID
- `VERCEL_ORG_ID` - Vercel organization ID
- `RAILWAY_TOKEN` - Railway deployment token
- `RESEND_API_KEY` - Resend email API key
- `TYPEFORM_API_KEY` - Typeform API key (for NPS)
- `TYPEFORM_FORM_ID` - Typeform form ID
- `ADMIN_SECRET` - Admin authentication secret
- `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY` - Clerk auth key
- `CLERK_SECRET_KEY` - Clerk secret key

## Crawlers (pipeline/crawlers/)

The following crawlers are configured in `scraper.yml`:

- `brazil_store.py` - Brazil Pickleball Store
- `dropshot_brasil.py` - Drop Shot Brasil
- `mercado_livre.py` - Mercado Livre

## Verification

All workflows have been validated:
- ✅ YAML syntax is valid
- ✅ Python version is consistent (3.12)
- ✅ File references exist
- ✅ No duplicate workflows
