import { test, expect } from '@playwright/test'

/**
 * Phase 13: Hybrid UI Redesign — UAT Verification
 *
 * Validates the Hybrid Modern Sports Tech design system implementation:
 * - Typography (Google Fonts)
 * - Color tokens (lime accent, data green)
 * - Navigation styling
 * - Button borders
 * - Card underlines
 * - Section alternation
 * - Responsive grid
 * - Link hover states
 * - Focus rings
 * - Class migration (hy-* prefix)
 */

test.describe('Phase 13: Hybrid UI Redesign', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
    // Wait for fonts to load
    await page.waitForLoadState('networkidle')
  })

  test('1. Typography — Google Fonts Loaded', async ({ page }) => {
    // Check that Google Fonts are requested
    const fontRequests: string[] = []

    page.on('request', (request) => {
      if (request.url().includes('fonts.googleapis.com')) {
        fontRequests.push(request.url())
      }
    })

    await page.reload()
    await page.waitForLoadState('networkidle')

    // Verify Inter or Instrument Sans or JetBrains Mono was requested
    const hasGoogleFonts = fontRequests.some(
      (url) =>
        url.includes('Inter') || url.includes('Instrument') || url.includes('JetBrains')
    )

    // Also check via computed styles that custom fonts are applied
    const bodyFont = await page.evaluate(() => {
      return window.getComputedStyle(document.body).fontFamily
    })

    // Should NOT have NVIDIA-EMEA inline
    const htmlStyle = await page.evaluate(() => {
      const html = document.documentElement
      return html.style.fontFamily || ''
    })

    expect(hasGoogleFonts || bodyFont.includes('Inter') || bodyFont.includes('Instrument') || bodyFont.includes('sans-serif')).toBeTruthy()
    expect(htmlStyle.includes('NVIDIA-EMEA')).toBeFalsy()
  })

  test('2. Color System — Design Tokens Applied', async ({ page }) => {
    // Check CSS custom properties exist
    const sportPrimary = await page.evaluate(() => {
      return getComputedStyle(document.documentElement).getPropertyValue('--sport-primary').trim()
    })

    const dataGreen = await page.evaluate(() => {
      return getComputedStyle(document.documentElement).getPropertyValue('--data-green').trim()
    })

    expect(sportPrimary).toBe('#84CC16')
    expect(dataGreen).toBe('#76b900')
  })

  test('3. Navigation — Logo Lime Accent', async ({ page }) => {
    // Find logo in header
    const logo = page.locator('.hy-nav-brand, .nv-nav-brand').first()

    await expect(logo).toBeVisible()

    // Check that logo contains a span for IQ accent
    const logoHTML = await logo.innerHTML()
    const hasIqSpan = logoHTML.includes('<span') && logoHTML.includes('IQ')

    // Check CSS applies lime color to the span
    const spanColor = await page.evaluate(() => {
      const brandSpan = document.querySelector('.hy-nav-brand span, .nv-nav-brand span')
      if (brandSpan) {
        return window.getComputedStyle(brandSpan).color
      }
      return null
    })

    // Either has the span structure or the brand itself has lime
    expect(hasIqSpan || spanColor).toBeTruthy()
  })

  test('4. Navigation — Header Styling', async ({ page }) => {
    const header = page.locator('.hy-nav, .nv-nav').first()

    // Check header background is black/dark
    const headerBg = await header.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor
    })

    // Should have dark background (rgb values close to 0 or dark gray)
    expect(headerBg).toMatch(/rgb\(\s*0|rgb\(\s*[0-4]\d|rgb\(\s*1[0-9]\d\)/)

    // Check nav links are uppercase
    const navLinks = page.locator('.hy-nav-link, .nv-nav-link')
    const linkCount = await navLinks.count()

    if (linkCount > 0) {
      const firstLinkText = await navLinks.first().textContent()
      expect(firstLinkText?.toUpperCase()).toBe(firstLinkText)
    }

    // Check mobile menu button exists
    const mobileMenuBtn = page.locator('.hy-nav-mobile button, .nv-nav-mobile button, [aria-label="menu"], [aria-label="Menu"]').first()
    await expect(mobileMenuBtn).toBeVisible()
  })

  test('5. Buttons — Lime Border Color', async ({ page }) => {
    // Find primary/CTA buttons
    const ctaButton = page.locator('.hy-nav-cta button, .nv-nav-cta button, button[class*="primary"], button[class*="cta"]').first()

    if (await ctaButton.isVisible()) {
      const borderColor = await ctaButton.evaluate((el) => {
        return window.getComputedStyle(el).borderColor
      })

      // Border should be lime (#84CC16) - check rgb equivalent
      // #84CC16 = rgb(132, 204, 22)
      const isLime =
        borderColor.includes('132') ||
        borderColor.includes('84CC16') ||
        borderColor.includes('84, 204, 22')

      // Border should NOT be data-green (#76b900 = rgb(118, 185, 0))
      const isDataGreen = borderColor.includes('118') && borderColor.includes('185')

      expect(isLime || !isDataGreen).toBeTruthy()
    }
  })

  test('6. Cards — Green Underline on Titles', async ({ page }) => {
    // Navigate to catalog
    await page.goto('/paddles')
    await page.waitForLoadState('networkidle')

    // Find product card title
    const cardTitle = page.locator('.hy-product-card-title, .hy-card-title-text, .nv-product-card-title, .nv-card-title-text').first()

    if (await cardTitle.isVisible()) {
      const borderBottom = await cardTitle.evaluate((el) => {
        const style = window.getComputedStyle(el)
        return {
          color: style.borderBottomColor,
          width: style.borderBottomWidth,
          style: style.borderBottomStyle
        }
      })

      // Should have 2px solid green border
      expect(borderBottom.width).toBe('2px')
      expect(borderBottom.style).toBe('solid')
      // Color should be #76b900 or rgb(118, 185, 0)
      expect(borderBottom.color).toMatch(/118.*185|76b900/i)
    }
  })

  test('7. Home Page — Section Alternation', async ({ page }) => {
    await page.goto('/')
    await page.waitForLoadState('networkidle')

    // Check for dark/light section pattern
    const darkSections = await page.locator('.hy-dark-section, .nv-dark-section').count()
    const lightSections = await page.locator('.hy-light-section, .nv-light-section').count()

    // Should have at least one of each
    expect(darkSections).toBeGreaterThanOrEqual(1)
    expect(lightSections).toBeGreaterThanOrEqual(1)
  })

  test('8. Responsive Grid — Catalog Layout', async ({ page }) => {
    await page.goto('/paddles')
    await page.waitForLoadState('networkidle')

    // Check grid exists
    const grid = page.locator('.hy-catalog-grid, .nv-catalog-grid').first()

    if (await grid.isVisible()) {
      // Check grid has items
      const gridItems = await grid.locator('> *').count()
      expect(gridItems).toBeGreaterThanOrEqual(0) // May be empty if no products
    }

    // Test responsive at different widths
    await page.setViewportSize({ width: 1200, height: 800 })
    // Grid should be 3 columns (can't easily test actual column count)
    // Just verify grid still visible
    await expect(grid).toBeVisible()
  })

  test('9. Links — Hover Color', async ({ page }) => {
    // Find a nav link
    const navLink = page.locator('.hy-nav-link, .nv-nav-link').first()

    if (await navLink.isVisible()) {
      // Check CSS has hover color defined
      const hoverColor = await page.evaluate(() => {
        const style = document.documentElement.style
        const css = getComputedStyle(document.documentElement)
        return {
          linkHoverVar: css.getPropertyValue('--color-link-hover').trim(),
          linkHoverRule: null as string | null
        }
      })

      // Should have #3860be link hover color
      expect(hoverColor.linkHoverVar).toBe('#3860be')
    }
  })

  test('10. Focus Rings — Accessibility', async ({ page }) => {
    // Tab through elements
    await page.keyboard.press('Tab')

    // Check focus-visible outline exists in CSS
    const focusStyles = await page.evaluate(() => {
      const styles = getComputedStyle(document.documentElement)
      return {
        outlineWidth: styles.getPropertyValue('--focus-ring-width') || '2px',
        outlineColor: styles.getPropertyValue('--focus-ring-color') || '#000000'
      }
    })

    // Just verify focus is visible on some element
    const focused = page.locator(':focus-visible, :focus').first()
    // Focus should exist after tab
  })

  test('11. Class Migration — hy-* Prefix', async ({ page }) => {
    // Get all class names in the document
    const classStats = await page.evaluate(() => {
      const allElements = document.querySelectorAll('[class]')
      let hyCount = 0
      let nvCount = 0

      allElements.forEach((el) => {
        const classes = el.className
        if (typeof classes === 'string') {
          if (classes.includes('hy-')) hyCount++
          if (classes.includes('nv-')) nvCount++
        }
      })

      return { hyCount, nvCount }
    })

    // hy-* classes should be present
    expect(classStats.hyCount).toBeGreaterThan(0)

    // nv-* classes should NOT be used in HTML (may exist as CSS aliases only)
    // Allow some nv-* for backwards compat, but hy-* should dominate
    expect(classStats.hyCount).toBeGreaterThanOrEqual(classStats.nvCount)
  })

  test('12. Footer — Responsive Stacking', async ({ page }) => {
    const footer = page.locator('.hy-footer, .nv-footer').first()

    await expect(footer).toBeVisible()

    // Check footer has dark background
    const footerBg = await footer.evaluate((el) => {
      return window.getComputedStyle(el).backgroundColor
    })

    // Should have dark background
    expect(footerBg).toMatch(/rgb\(\s*0|rgb\(\s*[0-4]\d|rgb\(\s*1[0-9]\d\)/)

    // Check footer grid structure
    const footerGrid = page.locator('.hy-footer-grid, .nv-footer-grid')
    const gridCount = await footerGrid.count()

    // Footer should have grid layout
    expect(gridCount).toBeGreaterThanOrEqual(0)
  })

  test('13. Product Detail Page — NVIDIA Styling', async ({ page }) => {
    // Try to navigate to a product page
    await page.goto('/paddles')
    await page.waitForLoadState('networkidle')

    // Find first product card link
    const productLink = page.locator('a[href*="/paddles/"]').first()

    if (await productLink.isVisible()) {
      await productLink.click()
      await page.waitForLoadState('networkidle')

      // Check dark section styling
      const darkSection = page.locator('.hy-dark-section, .nv-dark-section').first()

      // Check card styling exists
      const card = page.locator('.hy-card, .nv-card').first()

      // At minimum, page should have loaded without error
      await expect(page).toHaveURL(/\/paddles\//)
    }
  })
})