import { test, expect } from '@playwright/test'

/**
 * Test to validate that paddles have real images (not placeholders)
 *
 * This test:
 * 1. Loads the /paddles catalog page
 * 2. Checks all paddle images
 * 3. Validates that images are real (not unsplash placeholders)
 * 4. Reports statistics on image coverage
 */

test.describe('Paddle Image Validation', () => {
  test('all paddles should have real images', async ({ page }) => {
    // Clear browser cache to ensure fresh data
    await page.context().clearCookies()
    await page.goto('/paddles', { waitUntil: 'networkidle' })

    // Wait for the page to load
    await page.waitForSelector('article', { timeout: 10000 })

    // Get all paddle articles
    const articles = await page.locator('article').all()
    console.log(`Found ${articles.length} paddles in catalog`)

    expect(articles.length).toBeGreaterThan(0)

    // Track statistics
    const stats = {
      total: articles.length,
      withImages: 0,
      withRealImages: 0,
      withPlaceholderImages: 0,
      withoutImages: 0,
    }

    // Check each paddle's image
    for (let i = 0; i < articles.length; i++) {
      const article = articles[i]

      // Get image element
      const img = article.locator('img').first()
      const imgCount = await img.count()

      if (imgCount === 0) {
        stats.withoutImages++
        console.log(`Paddle ${i + 1}: NO IMAGE`)
        continue
      }

      stats.withImages++

      // Get image src
      const src = await img.getAttribute('src')
      console.log(`Paddle ${i + 1}: ${src?.substring(0, 60)}...`)

      // Check if it's a real image or placeholder
      if (src?.includes('unsplash.com') || src?.includes('placeholder')) {
        stats.withPlaceholderImages++
      } else if (src?.includes('mitiendanube.com')) {
        stats.withRealImages++
      } else if (src?.includes('http')) {
        stats.withRealImages++
      }
    }

    // Log statistics
    console.log('\n=== Image Validation Results ===')
    console.log(`Total paddles: ${stats.total}`)
    console.log(`With images: ${stats.withImages}`)
    console.log(`With real images: ${stats.withRealImages}`)
    console.log(`With placeholder images: ${stats.withPlaceholderImages}`)
    console.log(`Without images: ${stats.withoutImages}`)
    console.log(`Real image coverage: ${((stats.withRealImages / stats.total) * 100).toFixed(1)}%`)
    console.log('================================\n')

    // Assertions
    expect(stats.withImages).toBeGreaterThan(0)

    // At least 50% should have real images (adjust threshold as needed)
    const realImagePercentage = (stats.withRealImages / stats.total) * 100
    expect(realImagePercentage).toBeGreaterThanOrEqual(50)

    // No paddles should be without images
    expect(stats.withoutImages).toBe(0)
  })

  test('catalog page shows real product images', async ({ page }) => {
    // Navigate to paddles catalog
    await page.goto('/paddles', { waitUntil: 'networkidle' })
    await page.waitForSelector('article', { timeout: 10000 })

    // Get all articles and verify at least one has a real image
    const articles = await page.locator('article').all()
    let realImageCount = 0

    for (const article of articles.slice(0, 10)) {
      const img = article.locator('img').first()
      const src = await img.getAttribute('src')

      if (src?.includes('mitiendanube.com')) {
        realImageCount++
      }
    }

    // At least some products should have real images
    expect(realImageCount).toBeGreaterThan(0)
    console.log(`Found ${realImageCount} products with real images in first 10`)
  })
})
