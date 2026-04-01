import { chromium } from 'playwright'

async function debugCatalog() {
  const browser = await chromium.launch({ headless: true })
  const page = await browser.newPage()

  const PORT = process.env.PORT || '3000'
  console.log(`🔍 Navegando para http://localhost:${PORT}/paddles...`)
  await page.goto(`http://localhost:${PORT}/paddles`, { waitUntil: 'networkidle' })

  // Screenshot
  await page.screenshot({ path: 'debug-paddles.png' })
  console.log('📸 Screenshot salvo em debug-paddles.png')

  // Check 404
  const h1 = await page.textContent('h1').catch(() => null)
  console.log('H1:', h1)

  // Check title
  const title = await page.title()
  console.log('Title:', title)

  // Check for paddles or empty message
  const noPaddles = await page.textContent('text=Nenhuma raquete encontrada').catch(() => null)
  if (noPaddles) {
    console.log('⚠️  Catálogo vazio: "Nenhuma raquete encontrada"')
  } else {
    const cards = await page.locator('article').count()
    console.log(`✅ ${cards} raquetes encontradas no catálogo`)
  }

  // Check API calls
  console.log('\n📡 Requests de API:')
  page.on('response', res => {
    const url = res.url()
    if (url.includes('paddles') || url.includes('api')) {
      console.log(`  ${res.status()} - ${url}`)
    }
  })

  // Reload to capture requests
  await page.reload({ waitUntil: 'networkidle' })

  await browser.close()
}

debugCatalog().catch(console.error)
