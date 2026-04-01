import { test, expect } from '@playwright/test'

test.describe('Phase 08: Navigation UX Fixes - UAT Validation', () => {
  const BASE_URL = 'http://localhost:3000'

  test('1. Catalog card numeric-ID fallback (no 404)', async ({ page }) => {
    // Navegar para /paddles
    await page.goto(`${BASE_URL}/paddles`, { waitUntil: 'networkidle' })

    // Aguardar cards estarem presentes
    await page.waitForSelector('article', { state: 'visible', timeout: 10000 })

    // Encontrar todos os cards
    const cards = await page.locator('article').all()
    expect(cards.length).toBeGreaterThan(0)

    // Clicar no primeiro card
    const firstCard = cards[0]
    const cardHref = await firstCard.locator('a').first().getAttribute('href')

    console.log(`Card href: ${cardHref}`)

    // Navegar para página de detalhe
    await firstCard.click()

    // Aguardar navegação
    await page.waitForLoadState('networkidle')

    // Verificar que NÃO é 404
    const h1 = await page.locator('h1').first().textContent({ timeout: 5000 })
    console.log(`H1 text: ${h1}`)

    // 404 pages typically have "404" in the title or heading
    const is404Page = h1?.includes('404') || h1?.toLowerCase().includes('not found')
    expect(is404Page).toBeFalsy()

    // Verificar que a página de produto carregou
    const url = page.url()
    console.log(`Product page URL: ${url}`)

    // Deve conter detalhes do produto (nome, preço, etc)
    const hasProductInfo = await page.locator('text=/[R$\\$]/').isVisible({ timeout: 5000 })
      .catch(() => false)

    console.log(`Has product info (price): ${hasProductInfo}`)

    // Screenshot para evidência
    await page.screenshot({ path: '08-uat-1-product-page.png' })

    expect(hasProductInfo).toBeTruthy()
  })

  test('2. Header nav structure (desktop + mobile)', async ({ page }) => {
    // Testar desktop
    await page.setViewportSize({ width: 1280, height: 720 })
    await page.goto(`${BASE_URL}/`, { waitUntil: 'networkidle' })

    // Aguardar header estar visível
    await page.waitForSelector('header', { state: 'visible', timeout: 5000 })

    // Encontrar todos os links de navegação no header
    const navLinks = await page.locator('header a').allTextContents()
    console.log(`Desktop nav links: ${navLinks}`)

    // Verificar que existem "Home" e "Catalogo" como links de texto
    const hasHome = navLinks.some(link => link.includes('Home'))
    const hasCatalogo = navLinks.some(link => link.includes('Catalogo') || link.includes('Catálogo'))

    console.log(`Has Home: ${hasHome}, Has Catalogo: ${hasCatalogo}`)
    expect(hasHome).toBeTruthy()
    expect(hasCatalogo).toBeTruthy()

    // Verificar que NÃO tem "Chat IA" como link standalone
    const hasChatIA = navLinks.some(link =>
      link.toLowerCase().includes('chat') && link.toLowerCase().includes('ia')
    )
    console.log(`Has Chat IA link: ${hasChatIA}`)
    expect(hasChatIA).toBeFalsy()

    // Verificar botão "Encontrar raquete"
    const encontrarBtn = await page.locator('header button, header a').filter({ hasText: /Encontrar.*raquete/i }).count()
    console.log(`"Encontrar raquete" button count: ${encontrarBtn}`)

    // Screenshot desktop
    await page.screenshot({ path: '08-uat-2-header-desktop.png' })

    // Testar mobile
    await page.setViewportSize({ width: 375, height: 667 })
    await page.reload({ waitUntil: 'networkidle' })

    // Aguardar menu hamburger
    const hamburgerBtn = await page.locator('button[aria-label*="menu"], button[aria-label*="Menu"]').first()
    if (await hamburgerBtn.isVisible()) {
      await hamburgerBtn.click()
      await page.waitForTimeout(500)

      // Verificar links no menu mobile
      const mobileNavLinks = await page.locator('nav a, [role="navigation"] a').allTextContents()
      console.log(`Mobile nav links: ${mobileNavLinks}`)

      const mobileHasHome = mobileNavLinks.some(link => link.includes('Home'))
      const mobileHasCatalogo = mobileNavLinks.some(link => link.includes('Catalogo') || link.includes('Catálogo'))
      const mobileHasChatIA = mobileNavLinks.some(link =>
        link.toLowerCase().includes('chat') && link.toLowerCase().includes('ia')
      )

      console.log(`Mobile - Home: ${mobileHasHome}, Catalogo: ${mobileHasCatalogo}, Chat IA: ${mobileHasChatIA}`)

      expect(mobileHasHome).toBeTruthy()
      expect(mobileHasCatalogo).toBeTruthy()
      expect(mobileHasChatIA).toBeFalsy()
    }

    // Screenshot mobile
    await page.screenshot({ path: '08-uat-2-header-mobile.png' })
  })

  test('3. Catalog card spec enrichment visible', async ({ page }) => {
    await page.goto(`${BASE_URL}/paddles`, { waitUntil: 'networkidle' })

    // Aguardar cards estarem presentes
    await page.waitForSelector('article', { state: 'visible', timeout: 10000 })

    const cards = await page.locator('article').all()
    console.log(`Found ${cards.length} paddle cards`)

    let hasSkillLevelBadge = false
    let hasSpecsRow = false
    let hasStockIndicator = false

    for (const card of cards) {
      // Verificar skill_level badge (colorido)
      const skillLevelBadge = await card.locator('[class*="skill"], [class*="level"], text=/Beginner|Intermediate|Advanced/i').isVisible()
        .catch(() => false)

      if (skillLevelBadge) {
        hasSkillLevelBadge = true
        console.log('Found skill_level badge')
      }

      // Verificar specs row (SW: X, Core: Ymm)
      const specsText = await card.textContent() || ''
      const hasSwMatch = /SW:\s*\d+/i.test(specsText)
      const hasCoreMatch = /Core:\s*\d+mm/i.test(specsText)

      if (hasSwMatch || hasCoreMatch) {
        hasSpecsRow = true
        console.log(`Found specs: SW=${hasSwMatch}, Core=${hasCoreMatch}`)
      }

      // Verificar stock indicator
      const stockIndicator = await card.locator('[class*="stock"], text=/in stock|available|em estoque/i').isVisible()
        .catch(() => false)

      if (stockIndicator) {
        hasStockIndicator = true
        console.log('Found stock indicator')
      }

      // Se já encontrou pelo menos um, pode parar
      if (hasSkillLevelBadge || hasSpecsRow || hasStockIndicator) {
        break
      }
    }

    console.log(`Results: skill_level=${hasSkillLevelBadge}, specs=${hasSpecsRow}, stock=${hasStockIndicator}`)

    // Screenshot
    await page.screenshot({ path: '08-uat-3-card-enrichment.png' })

    // Pelo menos um dos três deve estar presente
    const hasEnrichment = hasSkillLevelBadge || hasSpecsRow || hasStockIndicator
    expect(hasEnrichment).toBeTruthy()
  })
})
