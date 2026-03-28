---
phase: 05-seo-growth-features
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - app/middleware.ts
  - app/layout.tsx
  - app/api/price-alerts/route.ts
  - app/api/users/migrate/route.ts
  - lib/clerk.ts
  - lib/resend.ts
  - components/clerk-provider.tsx
  - frontend/.env.local
autonomous: false
requirements: [R5.2]
user_setup:
  - service: Clerk
    why: "Authentication infrastructure for user persistence, session management"
    env_vars:
      - name: NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY
        source: "Clerk Dashboard -> Developers -> API Keys -> Publishable Key"
      - name: CLERK_SECRET_KEY
        source: "Clerk Dashboard -> Developers -> API Keys -> Secret Key"
    dashboard_config:
      - task: "Create application in Clerk"
        location: "Clerk Dashboard -> Applications"
      - task: "Enable Passkey & Email/Password auth methods"
        location: "Clerk Dashboard -> Configure -> Authentication methods"
  - service: Resend
    why: "Transactional email delivery for price alerts"
    env_vars:
      - name: RESEND_API_KEY
        source: "Resend Dashboard -> API Keys"
    dashboard_config:
      - task: "Add domain (alerts@pickleiq.com)"
        location: "Resend Dashboard -> Domains"

must_haves:
  truths:
    - "Anonymous user can access chat without login"
    - "User can sign up and log in via Clerk"
    - "Authenticated user profile persists after logout/login"
    - "User can create price alert (requires login)"
    - "Price alert email sends with unsubscribe header"
  artifacts:
    - path: "app/middleware.ts"
      provides: "clerkMiddleware() routing auth context globally"
      min_lines: 10
    - path: "app/layout.tsx"
      provides: "ClerkProvider wrapping entire app"
      min_lines: 5
    - path: "app/api/price-alerts/route.ts"
      provides: "POST /api/price-alerts protected endpoint"
      exports: ["POST"]
    - path: "lib/clerk.ts"
      provides: "Helper functions for Clerk auth checks"
      min_lines: 20
    - path: "lib/resend.ts"
      provides: "sendPriceAlert() email template function"
      min_lines: 30
  key_links:
    - from: "app/middleware.ts"
      to: "app/layout.tsx"
      via: "ClerkProvider receives auth context from middleware"
      pattern: "clerkMiddleware"
    - from: "app/api/price-alerts/route.ts"
      to: "lib/clerk.ts"
      via: "Route Handler calls auth() to verify userId"
      pattern: "import.*clerk"
    - from: "app/api/price-alerts/route.ts"
      to: "backend FastAPI"
      via: "POST request to create alert in database"
      pattern: "fetch.*price-alerts"

---

<objective>
**Phase Goal:** Integrate Clerk v5 authentication to replace anonymous sessions with persistent user accounts, enabling price alerts via email. Users log in once, their profile and chat history persist. Price alert system validates authentication, sends transactional emails via Resend with RFC 8058 compliance.

**Purpose:** Unlock personalization (saved favorites, price targets) and growth (email marketing). Phase 5 is growth-focused: SEO pages drive traffic, auth enables conversion, email drives retention.

**Output:**
- Clerk middleware + root layout configured
- Price alert creation requires login
- Email templates with unsubscribe headers
- Session upgrade path (anon → authenticated) documented
</objective>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
@$HOME/.claude/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/05-seo-growth-features/05-RESEARCH.md

# Key interfaces from Phase 4 (existing frontend)

From frontend/src/app/layout.tsx:
- Root layout uses Tailwind + shadcn/ui
- No auth provider currently

From backend FastAPI (Phase 2):
- POST /price-alerts expects { paddle_id, price_target, user_id }
- Returns { id, created_at, price_target }

From frontend/src/lib/api.ts (existing):
- fetch wrapper with NEXT_PUBLIC_FASTAPI_URL env var
- Graceful error handling returning empty []
</context>

<tasks>

<task type="checkpoint:decision" gate="blocking">
  <name>Checkpoint: Clerk Setup & Credentials Ready</name>
  <decision>Verify Clerk application created and API keys obtained before implementation</decision>
  <context>
    Clerk authentication requires two API keys (Publishable + Secret) from Clerk Dashboard.
    Without these, Route Handlers cannot authenticate users.
    This checkpoint prevents blocked implementation waiting for async signup.
  </context>
  <options>
    <option id="option-create">
      <name>Create Clerk app now</name>
      <pros>Unblocks implementation immediately; credentials ready for middleware setup</pros>
      <cons>Requires ~5 min in Clerk Dashboard</cons>
    </option>
    <option id="option-pause">
      <name>Pause, create later</name>
      <pros>Can return to this plan after Clerk signup</pros>
      <cons>Plan cannot execute until credentials available</cons>
    </option>
  </options>
  <resume-signal>Provide NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY and CLERK_SECRET_KEY (or confirm option-pause)</resume-signal>
</task>

<task type="auto" tdd="true">
  <name>Task 1: Set up Clerk middleware and root layout</name>
  <files>
    app/middleware.ts
    app/layout.tsx
    frontend/.env.local
    frontend/__tests__/clerk-middleware.test.ts
  </files>
  <behavior>
    - Middleware exports clerkMiddleware() from @clerk/nextjs/server
    - ClerkProvider wraps root layout children
    - API routes can access auth() from @clerk/nextjs/server
    - Anonymous user can navigate without login
    - Authenticated user has userId available in Route Handlers
  </behavior>
  <action>
    1. Add Clerk dependencies: `npm install @clerk/nextjs@5.0.0` in frontend/
    2. Create `app/middleware.ts`:
       ```typescript
       import { clerkMiddleware } from '@clerk/nextjs/server';
       export default clerkMiddleware();
       export const config = { matcher: ['/((?!.+\\.[\\w]+$|_next).*)', '/', '/(api|trpc)(.*)'] };
       ```
    3. Update `app/layout.tsx`:
       - Import ClerkProvider from @clerk/nextjs
       - Wrap {children} with `<ClerkProvider>{children}</ClerkProvider>`
    4. Create `lib/clerk.ts` with helper:
       ```typescript
       import { auth } from '@clerk/nextjs/server';
       export async function getUserId() {
         const { userId } = await auth();
         return userId;
       }
       ```
    5. Add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY and CLERK_SECRET_KEY to frontend/.env.local
    6. Test: `npm run build` should compile without errors
  </action>
  <verify>
    <automated>npm run build 2>&1 | grep -q "Compiled successfully" && npm run test -- --grep="clerk-middleware"</automated>
  </verify>
  <done>
    - Middleware exports clerkMiddleware() with correct config matcher
    - ClerkProvider wraps root layout
    - .env.local has both CLERK keys
    - Build succeeds with no auth-related warnings
    - Middleware test passes: anonymous user can access /, authenticated user has auth context
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Create protected price-alert endpoint with email setup</name>
  <files>
    app/api/price-alerts/route.ts
    lib/resend.ts
    components/price-alert-form.tsx
    frontend/__tests__/price-alerts.test.ts
    backend/tests/test_price_alerts_email.py
  </files>
  <behavior>
    - POST /api/price-alerts requires authenticated user (401 if anon)
    - Accepts { paddle_id, price_target } in request body
    - Calls auth() to retrieve userId
    - Forwards to backend FastAPI POST /price-alerts with { user_id, paddle_id, price_target }
    - Resend sendPriceAlert() generates email with unsubscribe header (RFC 8058)
    - Email template in Portuguese (PT-BR), includes product name and price
    - Email includes visible unsubscribe link in footer
  </behavior>
  <action>
    1. Install Resend: `npm install resend react-email` in frontend/
    2. Create `lib/resend.ts`:
       ```typescript
       import { Resend } from 'resend';

       const resend = new Resend(process.env.RESEND_API_KEY);

       export async function sendPriceAlert({
         email,
         paddleName,
         currentPrice,
         priceTarget,
         paddleUrl,
         userId,
       }: {
         email: string;
         paddleName: string;
         currentPrice: number;
         priceTarget: number;
         paddleUrl: string;
         userId: string;
       }) {
         return await resend.emails.send({
           from: 'alerts@pickleiq.com',
           to: email,
           subject: `Alerta de preço: ${paddleName}`,
           html: `<p>Ótima notícia! ${paddleName} agora custa R$ ${currentPrice.toFixed(2)} — abaixo do seu alvo de R$ ${priceTarget.toFixed(2)}.</p>
                  <p><a href="${paddleUrl}">Ver raquete</a></p>
                  <p style="font-size: 12px; color: #999; margin-top: 40px;">
                    <a href="https://pickleiq.com/api/unsubscribe?user_id=${userId}">Desinscrever</a>
                  </p>`,
           headers: {
             'List-Unsubscribe': `<https://pickleiq.com/api/unsubscribe?user_id=${userId}>`,
             'List-Unsubscribe-Post': 'List-Unsubscribe=One-Click',
           },
         });
       }
       ```
    3. Create `app/api/price-alerts/route.ts`:
       ```typescript
       import { auth } from '@clerk/nextjs/server';
       import { NextResponse } from 'next/server';

       export async function POST(req: Request) {
         const { userId } = await auth();

         if (!userId) {
           return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
         }

         const { paddle_id, price_target } = await req.json();

         const backendUrl = process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://localhost:8000';
         const res = await fetch(`${backendUrl}/price-alerts`, {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({ user_id: userId, paddle_id, price_target }),
         });

         if (!res.ok) return NextResponse.json({ error: 'Failed to create alert' }, { status: 500 });

         const alert = await res.json();
         return NextResponse.json(alert, { status: 201 });
       }
       ```
    4. Create React Email template `components/price-alert-email.tsx` (reusable for future email variations)
    5. Add RESEND_API_KEY to frontend/.env.local
    6. Test: Price alert POST requires auth, returns 201, email payload has RFC 8058 headers
  </action>
  <verify>
    <automated>npm run test -- --grep="price-alerts" && pytest backend/tests/test_price_alerts_email.py -xvs</automated>
  </verify>
  <done>
    - POST /api/price-alerts returns 401 for anonymous user
    - POST /api/price-alerts returns 201 for authenticated user with alert object
    - Email template includes unsubscribe header per RFC 8058
    - Email body includes visible unsubscribe link + product details
    - Frontend test mocks Clerk auth, verifies 401/201 responses
    - Backend test verifies email payload structure
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 3: Anon-to-auth migration endpoint (session upgrade)</name>
  <files>
    app/api/users/migrate/route.ts
    lib/profile.ts
    frontend/__tests__/session-upgrade.test.ts
    backend/tests/test_user_migration.py
  </files>
  <behavior>
    - Anonymous user has profile saved in localStorage with UUID key
    - After login, app calls POST /api/users/migrate with { old_uuid, new_user_id }
    - Backend reconciles chat history: merges old_uuid messages into new_user_id account
    - Frontend clears old localStorage profile, sets new localStorage['pickleiq:user_id'] = new_user_id
    - User never loses quiz profile or chat history across login
  </behavior>
  <action>
    1. Create `app/api/users/migrate/route.ts`:
       ```typescript
       import { auth } from '@clerk/nextjs/server';
       import { NextResponse } from 'next/server';

       export async function POST(req: Request) {
         const { userId } = await auth();
         if (!userId) return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });

         const { old_uuid } = await req.json();

         const backendUrl = process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://localhost:8000';
         const res = await fetch(`${backendUrl}/users/migrate`, {
           method: 'POST',
           headers: { 'Content-Type': 'application/json' },
           body: JSON.stringify({ old_uuid, new_user_id: userId }),
         });

         if (!res.ok) return NextResponse.json({ error: 'Migration failed' }, { status: 500 });

         return NextResponse.json({ success: true });
       }
       ```
    2. Create `lib/profile.ts` with client-side migration logic:
       ```typescript
       export async function migrateProfileOnLogin(oldUUID: string, newUserId: string) {
         const res = await fetch('/api/users/migrate', {
           method: 'POST',
           body: JSON.stringify({ old_uuid: oldUUID, new_user_id: newUserId }),
         });
         if (!res.ok) throw new Error('Migration failed');

         // Clear old localStorage, set new
         localStorage.removeItem(`pickleiq:profile:${oldUUID}`);
         localStorage.setItem('pickleiq:user_id', newUserId);
       }
       ```
    3. In `app/layout.tsx` or sign-in page, hook Clerk's `useEffect(() => { if (isSignedIn && hasOldProfile) migrateProfileOnLogin(...) })`
    4. Test: Anonymous user creates chat, logs in, migration succeeds, chat history persists
  </action>
  <verify>
    <automated>npm run test -- --grep="session-upgrade" && pytest backend/tests/test_user_migration.py -xvs</automated>
  </verify>
  <done>
    - Migration endpoint requires authentication (401 if anon)
    - POST /api/users/migrate reconciles old_uuid messages into new_user_id
    - Frontend localStorage updated: old profile cleared, user_id set
    - Chat history accessible after login
    - Tests verify: no data loss, old UUID messages inaccessible post-migration
  </done>
</task>

<task type="checkpoint:human-verify" gate="blocking">
  <name>Checkpoint: Clerk Auth & Email Flow Verification</name>
  <what-built>
    - Clerk v5 middleware + layout
    - Protected /api/price-alerts endpoint
    - Email setup with Resend
    - Session upgrade migration
  </what-built>
  <how-to-verify>
    1. **Anon access:** Visit https://localhost:3000 without signing in → quiz and chat accessible
    2. **Sign up:** Click "Sign in" → create account via Clerk email/passkey → redirected to dashboard
    3. **Create price alert:**
       - As authenticated user, click "Watch price" on any product
       - Enter price target (e.g., 200 BRL)
       - Confirm alert created (check frontend toast)
    4. **Email receipt:**
       - Monitor Resend dashboard or check backend logs for email send event
       - Verify email includes unsubscribe link in both header and footer
    5. **Session persistence:**
       - Log out, log back in
       - Verify chat history and profile still present
    6. **Auth check:**
       - Open browser DevTools → Network
       - Call `fetch('/api/price-alerts', { method: 'POST', body: JSON.stringify({ paddle_id: 1, price_target: 200 }) })`
       - Expect 401 in incognito tab (anon), 201 in signed-in tab (auth)
  </how-to-verify>
  <resume-signal>Type "approved" or describe issues (e.g., "email not sending", "401 not working", "localStorage not clearing")</resume-signal>
</task>

</tasks>

<verification>
**Phase 05-01 Completion Checks:**

1. **Auth infrastructure:**
   - [ ] Clerk middleware installed and configured
   - [ ] ClerkProvider wraps root layout
   - [ ] Middleware test passes (anon access, auth context)

2. **Email delivery:**
   - [ ] Resend API key configured
   - [ ] Email template renders with unsubscribe header (RFC 8058)
   - [ ] sendPriceAlert() function exports successfully

3. **Protected endpoints:**
   - [ ] POST /api/price-alerts requires userId (returns 401 if anon)
   - [ ] POST /api/price-alerts returns 201 and alert object if authenticated
   - [ ] POST /api/users/migrate reconciles old profile into new account

4. **Data persistence:**
   - [ ] Chat history survives logout/login cycle
   - [ ] localStorage keys properly cleared after migration
   - [ ] New userId stored correctly post-migration

5. **Integration:**
   - [ ] Frontend can read Clerk user context
   - [ ] Route Handlers can call auth() without errors
   - [ ] Fetch to backend /price-alerts includes correct user_id
</verification>

<success_criteria>
Phase 05-01 succeeds when:
- Users can sign up and authenticate via Clerk
- Authenticated users can create price alerts
- Price alerts trigger email sends via Resend
- Emails include RFC 8058 unsubscribe headers
- Anonymous profiles migrate to authenticated accounts without data loss
- All tests pass: `npm run test && pytest tests/test_price_alerts.py -x`
</success_criteria>

<output>
After completion, create `.planning/phases/05-seo-growth-features/05-01-SUMMARY.md` with:
- Clerk setup details (app name, OAuth provider list)
- Email template version and send counts
- Migration test results (success rate, edge cases)
- Blockers and workarounds encountered
</output>
