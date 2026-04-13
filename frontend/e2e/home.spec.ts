import { test, expect } from '@playwright/test'

test.describe('Home Page', () => {
  test('loads with correct page title', async ({ page }) => {
    await page.goto('/')
    await expect(page).toHaveTitle(/PickleIQ/)
  })

  test('renders hero section with main heading', async ({ page }) => {
    await page.goto('/')
    const heading = page.getByRole('heading', { level: 1 }).or(
      page.getByRole('heading', { level: 2 })
    )
    await expect(heading.first()).toBeVisible({ timeout: 10000 })
  })

  test('displays CTA links to quiz', async ({ page }) => {
    await page.goto('/')
    // Landing page has "ENCONTRAR MINHA RAQUETE" CTA buttons linking to /quiz
    const ctaLinks = page.getByRole('link', { name: /encontrar minha raquete/i })
    await expect(ctaLinks.first()).toBeVisible({ timeout: 10000 })
  })

  test('has no console errors on load', async ({ page }) => {
    const errors: string[] = []
    page.on('console', (msg) => {
      if (msg.type() === 'error') errors.push(msg.text())
    })
    await page.goto('/')
    await page.waitForLoadState('networkidle')
    const criticalErrors = errors.filter(
      (e) => !e.includes('favicon') && !e.includes('404') && !e.includes('net::ERR')
    )
    expect(criticalErrors).toHaveLength(0)
  })
})
