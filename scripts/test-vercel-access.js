const { chromium } = require('playwright');

async function test() {
  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage();
  const BASE = 'https://frontend-q7iq0qjkb-diegopereira93s-projects.vercel.app';

  const results = [];

  const check = async (path, label, fn) => {
    try {
      const res = await page.goto(BASE + path, { waitUntil: 'domcontentloaded', timeout: 15000 });
      const status = res?.status();
      const url = page.url();
      const pass = await fn(page, status, url);
      results.push({ label, status, url: url.replace(BASE,''), pass });
    } catch(e) {
      results.push({ label, status: 'ERR', url: path, pass: false, err: e.message.slice(0,60) });
    }
  };

  await check('/', 'Home page loads',
    async (p, s) => s === 200 && (await p.textContent('body'))?.includes('PickleIQ'));

  await check('/chat', '/chat accessible',
    async (p, s, u) => s === 200 && u.includes('/chat'));

  await check('/paddles', '/paddles accessible',
    async (p, s, u) => s === 200 && u.includes('/paddles'));

  await check('/blog/pillar-page', '/blog accessible',
    async (p, s) => s === 200);

  await check('/admin', '/admin accessible',
    async (p, s) => s !== 404);

  // Screenshot
  await page.goto(BASE, { waitUntil: 'networkidle', timeout: 15000 }).catch(()=>{});
  await page.screenshot({ path: 'scripts/vercel-ready.png', fullPage: false });

  await browser.close();

  console.log('\n=== Playwright Validation Results ===\n');
  let passed = 0;
  for (const r of results) {
    const icon = r.pass ? '✅' : '❌';
    console.log(`${icon} [${r.status}] ${r.label} → ${r.url}${r.err ? ' ERR: '+r.err : ''}`);
    if (r.pass) passed++;
  }
  console.log(`\nScore: ${passed}/${results.length}`);
}

test().catch(console.error);
