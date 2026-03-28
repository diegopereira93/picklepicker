import type { UserProfile } from '@/types/paddle'

const UID_KEY = 'pickleiq:uid'

export function getOrCreateUserId(): string {
  if (typeof window === 'undefined') return ''
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

export function getProfile(): UserProfile | null {
  if (typeof window === 'undefined') return null
  const raw = localStorage.getItem(profileKey())
  if (!raw) return null
  try {
    return JSON.parse(raw) as UserProfile
  } catch {
    return null
  }
}

export function saveProfile(profile: UserProfile): void {
  if (typeof window === 'undefined') return
  localStorage.setItem(profileKey(), JSON.stringify(profile))
}

export function clearProfile(): void {
  if (typeof window === 'undefined') return
  localStorage.removeItem(profileKey())
}
