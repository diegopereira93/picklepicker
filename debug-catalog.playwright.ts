import { test, expect } from '@playwright/test'

test.describe('Debug Catalogo Vazio - /paddles', () => {
  test('verificar se a página /paddles carrega sem 404', async ({ page }) => {
    // Navegar para /paddles
    await page.goto('http://localhost:3000/paddles', { waitUntil: 'networkidle' })

    // Tirar screenshot
    await page.screenshot({ path: 'debug-paddles-page.png' })

    // Verificar se não é 404
    const is404 = await page.textContent('h1')
    console.log('H1 text:', is404)
    expect(is404).not.toContain('404')

    // Verificar se o título da página está correto
    const title = await page.title()
    console.log('Page title:', title)
    expect(title).toContain('Raquetes')

    // Verificar se o heading H1 está presente
    const h1 = await page.textContent('h1')
    console.log('H1:', h1)
    expect(h1).toContain('Catálogo')

    // Verificar se há cards de raquetes ou mensagem de "nenhuma raquete"
    const noPaddles = await page.textContent('text=Nenhuma raquete encontrada')
    if (noPaddles) {
      console.log('⚠️  Catálogo vazio - Nenhuma raquete encontrada')
    } else {
      const cards = await page.locator('article').count()
      console.log(`✅ ${cards} raquetes encontradas`)
    }
  })

  test('verificar API response', async ({ page }) => {
    // Interceptar requests para a API
    const responses: any[] = []
    page.on('response', response => {
      if (response.url().includes('/paddles') || response.url().includes('/api')) {
        responses.push({
          url: response.url(),
          status: response.status(),
        })
        console.log(`API Response: ${response.status()} - ${response.url()}`)
      }
    })

    await page.goto('http://localhost:3000/paddles', { waitUntil: 'networkidle' })

    console.log('All API responses:', responses)
  })
})
