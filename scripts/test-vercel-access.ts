import { chromium } from 'playwright';

async function testVercelAccess() {
  const browser = await chromium.launch({ headless: true });
  const context = await browser.createBrowserContext();
  const page = await context.newPage();

  console.log('=== Testing picklepicker.vercel.app Access ===\n');

  try {
    // Test 1: Try to access home page
    console.log('1. Accessing https://picklepicker.vercel.app/');
    await page.goto('https://picklepicker.vercel.app/', { waitUntil: 'domcontentloaded', timeout: 10000 });

    const currentUrl = page.url();
    console.log(`   Current URL: ${currentUrl}`);

    // Check if redirected to login
    if (currentUrl.includes('clerk') || currentUrl.includes('sign-in') || currentUrl.includes('login')) {
      console.log('   ❌ REDIRECTED TO LOGIN PAGE');
      console.log(`   Redirect URL: ${currentUrl}`);

      // Take screenshot
      await page.screenshot({ path: 'scripts/login-screen.png' });
      console.log('   Screenshot saved: login-screen.png');
    } else {
      console.log('   ✅ Home page loaded (no redirect)');
    }

    // Check page title and content
    const title = await page.title();
    const pageContent = await page.textContent('body');
    console.log(`   Page title: ${title}`);

    if (pageContent?.includes('Access Unauthorized')) {
      console.log('   ❌ ERROR: "Access Unauthorized" message found');
    }

    if (pageContent?.includes('PickleIQ')) {
      console.log('   ✅ PickleIQ content visible');
    }

    console.log('\n2. Checking for Google Login button');
    const googleButton = await page.$('[data-testid="oauth_google"], button:has-text("Google"), a:has-text("Google")');
    if (googleButton) {
      console.log('   ✅ Google login button found');
    } else {
      console.log('   ❌ No Google button found');
    }

    console.log('\n3. Checking Clerk authentication setup');
    const clerkScripts = await page.$$eval('script', scripts =>
      scripts.filter(s => s.src && s.src.includes('clerk')).map(s => s.src)
    );
    if (clerkScripts.length > 0) {
      console.log(`   ✅ Clerk scripts loaded: ${clerkScripts.length} script(s)`);
      clerkScripts.forEach(src => console.log(`      - ${src}`));
    } else {
      console.log('   ⚠️  No Clerk scripts found');
    }

    console.log('\n4. Testing /chat endpoint');
    await page.goto('https://picklepicker.vercel.app/chat', { waitUntil: 'domcontentloaded', timeout: 10000 });
    const chatUrl = page.url();
    console.log(`   Current URL: ${chatUrl}`);
    if (chatUrl.includes('sign-in') || chatUrl.includes('clerk')) {
      console.log('   ❌ /chat also redirects to login');
    } else {
      console.log('   ✅ /chat is accessible');
    }

    console.log('\n5. Testing /paddles endpoint');
    await page.goto('https://picklepicker.vercel.app/paddles', { waitUntil: 'domcontentloaded', timeout: 10000 });
    const paddlesUrl = page.url();
    console.log(`   Current URL: ${paddlesUrl}`);
    if (paddlesUrl.includes('sign-in') || paddlesUrl.includes('clerk')) {
      console.log('   ❌ /paddles also redirects to login');
    } else {
      console.log('   ✅ /paddles is accessible');
    }

  } catch (error) {
    console.error('❌ Error during testing:', error instanceof Error ? error.message : String(error));
  } finally {
    await browser.close();
  }

  console.log('\n=== Summary ===');
  console.log('The application appears to have authentication enforced globally.');
  console.log('Next steps:');
  console.log('1. Check Clerk configuration in vercel.json env vars');
  console.log('2. Verify CLERK_SECRET_KEY is set correctly');
  console.log('3. Check middleware.ts for auth enforcement rules');
  console.log('4. Consider: Is auth intentional or a misconfiguration?');
}

testVercelAccess().catch(console.error);
