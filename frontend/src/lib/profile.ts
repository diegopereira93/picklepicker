import type { UserProfile } from '@/types/paddle'

const UID_KEY = 'pickleiq:uid'
const AUTH_USER_ID_KEY = 'pickleiq:user_id'
const AUTH_TOKEN_KEY = '__clerk_client_jwt'

function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null
  return localStorage.getItem(AUTH_TOKEN_KEY)
}

function isAuthenticated(): boolean {
  return !!getAuthToken()
}

export function getOrCreateUserId(): string {
  if (typeof window === 'undefined') return ''
  const authId = localStorage.getItem(AUTH_USER_ID_KEY)
  if (authId) return authId
  const existing = localStorage.getItem(UID_KEY)
  if (existing) return existing
  const uid = crypto.randomUUID()
  localStorage.setItem(UID_KEY, uid)
  return uid
}

function profileKey(): string {
  const uid = getOrCreateUserId()
  return `pickleiq:profile:${uid}`
}

export async function getProfile(): Promise<UserProfile | null> {
  if (typeof window === 'undefined') return null

  const authToken = getAuthToken()
  if (authToken) {
    try {
      const res = await fetch('/api/v1/users/profile/me', {
        headers: { Authorization: `Bearer ${authToken}` },
      })
      if (res.ok) {
        const data = await res.json()
        return {
          level: data.level,
          style: data.style,
          budget_max: data.budget_max,
        }
      }
    } catch {
    }
  }

  const raw = localStorage.getItem(profileKey())
  if (!raw) return null
  try {
    return JSON.parse(raw) as UserProfile
  } catch {
    return null
  }
}

export async function saveProfile(profile: UserProfile): Promise<void> {
  if (typeof window === 'undefined') return

  localStorage.setItem(profileKey(), JSON.stringify(profile))

  const authToken = getAuthToken()
  if (authToken) {
    try {
      await fetch('/api/v1/users/profile', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${authToken}`,
        },
        body: JSON.stringify({
          user_id: getOrCreateUserId(),
          level: profile.level,
          style: profile.style,
          budget_max: profile.budget_max,
        }),
      })
    } catch {
    }
  }
}

export function clearProfile(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem(profileKey())
}

export async function migrateProfileOnLogin(oldUUID: string, newUserId: string): Promise<void> {
  const authToken = getAuthToken()
  if (!authToken) {
    throw new Error('Not authenticated')
  }

  const res = await fetch('/api/v1/users/migrate', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${authToken}`,
    },
    body: JSON.stringify({ old_uuid: oldUUID, new_user_id: newUserId }),
  })

  if (!res.ok) {
    throw new Error('Migration failed')
  }

  localStorage.removeItem(`pickleiq:profile:${oldUUID}`)
  localStorage.setItem(AUTH_USER_ID_KEY, newUserId)
}
