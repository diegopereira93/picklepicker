# Deferred Items — Phase 04

## Pre-existing build failures (out of scope for 04-04)

### Missing: frontend/src/components/chat/chat-widget
- **Error:** `Module not found: Can't resolve '@/components/chat/chat-widget'`
- **File:** `frontend/src/app/chat/page.tsx`
- **Cause:** Scaffold stub created by 04-01, implementation deferred to plan 04-02 (Chat Widget)
- **Impact:** `npm run build` fails until 04-02 is executed
- **Resolution:** Will be resolved when 04-02 creates the chat-widget component
