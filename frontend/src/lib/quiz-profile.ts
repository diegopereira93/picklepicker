export interface QuizProfile {
  level: 'beginner' | 'intermediate' | 'advanced' | 'competitive'
  style: 'baseline-grinder' | 'dink-control' | 'power-hitter' | 'all-round'
  priority: 'control' | 'power' | 'spin' | 'speed'
  budget: 'under-80' | '80-150' | '150-250' | '250-plus'
  weightPreference: 'light' | 'medium' | 'heavy' | 'no-preference'
  location: 'indoor' | 'outdoor' | 'both'
  targetPaddle?: string
  completedAt: string
}

const STORAGE_KEY = 'pickleiq_player_profile'

export function saveQuizProfile(profile: QuizProfile): void {
  if (typeof window === 'undefined') return
  
  const profileWithTimestamp = {
    ...profile,
    completedAt: new Date().toISOString()
  }
  
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(profileWithTimestamp))
  } catch (error) {
    console.error('Failed to save quiz profile to localStorage:', error)
  }
}

export function loadQuizProfile(): QuizProfile | null {
  if (typeof window === 'undefined') return null
  
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    if (!stored) return null
    
    const parsed = JSON.parse(stored)
    
    return {
      level: parsed.level,
      style: parsed.style,
      priority: parsed.priority,
      budget: parsed.budget,
      weightPreference: parsed.weightPreference,
      location: parsed.location,
      targetPaddle: parsed.targetPaddle,
      completedAt: parsed.completedAt
    }
  } catch (error) {
    console.error('Failed to load quiz profile from localStorage:', error)
    return null
  }
}

export function clearQuizProfile(): void {
  if (typeof window === 'undefined') return
  
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch (error) {
    console.error('Failed to clear quiz profile from localStorage:', error)
  }
}

export function hasQuizProfile(): boolean {
  if (typeof window === 'undefined') return false
  
  try {
    return localStorage.getItem(STORAGE_KEY) !== null
  } catch (error) {
    console.error('Failed to check quiz profile in localStorage:', error)
    return false
  }
}

export function getProfileSummary(profile: QuizProfile): string[] {
  const levelLabels: Record<QuizProfile['level'], string> = {
    beginner: 'Beginner',
    intermediate: 'Intermediate',
    advanced: 'Advanced',
    competitive: 'Competitive'
  }
  
  const styleLabels: Record<QuizProfile['style'], string> = {
    'baseline-grinder': 'Baseline Grinder',
    'dink-control': 'Dink Control',
    'power-hitter': 'Power Hitter',
    'all-round': 'All-Round'
  }
  
  const priorityLabels: Record<QuizProfile['priority'], string> = {
    control: 'Priority: Control',
    power: 'Priority: Power',
    spin: 'Priority: Spin',
    speed: 'Priority: Speed'
  }
  
  const budgetLabels: Record<QuizProfile['budget'], string> = {
    'under-80': 'Under $80',
    '80-150': '$80-150',
    '150-250': '$150-250',
    '250-plus': '$250+'
  }
  
  return [
    levelLabels[profile.level],
    styleLabels[profile.style],
    priorityLabels[profile.priority],
    budgetLabels[profile.budget]
  ]
}

export function syncQuizProfileToDatabase(profile: QuizProfile, userId: string): Promise<boolean> {
  return fetch('/api/user/quiz-profile', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      userId,
      profile
    })
  })
  .then(response => response.ok)
  .catch(error => {
    console.error('Failed to sync quiz profile to database:', error)
    return false
  })
}

export async function loadQuizProfileWithFallback(userId?: string): Promise<QuizProfile | null> {
  if (userId) {
    try {
      const response = await fetch(`/api/user/quiz-profile?userId=${userId}`)
      if (response.ok) {
        const dbProfile = await response.json()
        return dbProfile as QuizProfile
      }
    } catch (error) {
      console.error('Failed to load quiz profile from database:', error)
    }
  }
  
  return loadQuizProfile()
}