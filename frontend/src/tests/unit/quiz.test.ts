import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import React from 'react'
import { getOrCreateUserId, getProfile, saveProfile } from '@/lib/profile'
import { QuizFlow } from '@/components/quiz/quiz-flow'

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {}
  return {
    getItem: (key: string) => store[key] ?? null,
    setItem: (key: string, value: string) => { store[key] = value },
    removeItem: (key: string) => { delete store[key] },
    clear: () => { store = {} },
  }
})()

Object.defineProperty(window, 'localStorage', { value: localStorageMock })
Object.defineProperty(window, 'crypto', {
  value: { randomUUID: vi.fn().mockReturnValue('test-uuid-1234') },
})

beforeEach(() => {
  localStorageMock.clear()
  vi.clearAllMocks()
})

describe('getOrCreateUserId', () => {
  it('Test 5: generates UUID on first call', () => {
    const uid = getOrCreateUserId()
    expect(uid).toBe('test-uuid-1234')
    expect(localStorageMock.getItem('pickleiq:uid')).toBe('test-uuid-1234')
  })

  it('Test 5b: returns same UUID on subsequent calls', () => {
    localStorageMock.setItem('pickleiq:uid', 'existing-uuid')
    const uid = getOrCreateUserId()
    expect(uid).toBe('existing-uuid')
  })
})

describe('getProfile / saveProfile', () => {
  it('Test 4: saves profile to localStorage under pickleiq:profile:{uid}', () => {
    localStorageMock.setItem('pickleiq:uid', 'myuid')
    saveProfile({ level: 'beginner', style: 'control', budget_max: 600 })
    const raw = localStorageMock.getItem('pickleiq:profile:myuid')
    expect(raw).not.toBeNull()
    const parsed = JSON.parse(raw!)
    expect(parsed).toEqual({ level: 'beginner', style: 'control', budget_max: 600 })
  })

  it('returns null when no profile stored', () => {
    localStorageMock.setItem('pickleiq:uid', 'myuid')
    expect(getProfile()).toBeNull()
  })

  it('returns stored profile', () => {
    localStorageMock.setItem('pickleiq:uid', 'myuid')
    saveProfile({ level: 'advanced', style: 'power', budget_max: 1000 })
    const profile = getProfile()
    expect(profile?.level).toBe('advanced')
    expect(profile?.budget_max).toBe(1000)
  })
})

describe('QuizFlow component', () => {
  function renderQuiz(onComplete = vi.fn()) {
    localStorageMock.setItem('pickleiq:uid', 'myuid')
    return render(React.createElement(QuizFlow, { onComplete }))
  }

  it('Test 1: renders step 1 (level) first', () => {
    renderQuiz()
    expect(screen.getByText(/qual o seu nivel de jogo/i)).toBeDefined()
  })

  it('Test 1b: advance button disabled without selection', () => {
    renderQuiz()
    const btn = screen.getByRole('button', { name: /proximo/i })
    expect(btn).toHaveProperty('disabled', true)
  })

  it('Test 2: selecting beginner enables advance button', () => {
    renderQuiz()
    fireEvent.click(screen.getByText('Iniciante'))
    const btn = screen.getByRole('button', { name: /proximo/i })
    expect(btn).toHaveProperty('disabled', false)
  })

  it('Test 2b: clicking Next after level selection shows step 2 (style)', () => {
    renderQuiz()
    fireEvent.click(screen.getByText('Iniciante'))
    fireEvent.click(screen.getByRole('button', { name: /proximo/i }))
    expect(screen.getByText(/qual seu estilo de jogo/i)).toBeDefined()
  })

  it('Test 8: advance blocked without selection at each step', () => {
    renderQuiz()
    // Step 1 - no selection
    expect(screen.getByRole('button', { name: /proximo/i }).getAttribute('disabled')).not.toBeNull()
    // Move to step 2
    fireEvent.click(screen.getByText('Iniciante'))
    fireEvent.click(screen.getByRole('button', { name: /proximo/i }))
    // Step 2 - no selection
    expect(screen.getByRole('button', { name: /proximo/i }).getAttribute('disabled')).not.toBeNull()
  })

  it('Test 3: completing all 3 steps calls saveProfile with correct data', () => {
    localStorageMock.setItem('pickleiq:uid', 'myuid')
    const onComplete = vi.fn()
    render(React.createElement(QuizFlow, { onComplete }))

    // Step 1: level
    fireEvent.click(screen.getByText('Iniciante'))
    fireEvent.click(screen.getByRole('button', { name: /proximo/i }))

    // Step 2: style
    fireEvent.click(screen.getByText('Controle'))
    fireEvent.click(screen.getByRole('button', { name: /proximo/i }))

    // Step 3: budget
    fireEvent.click(screen.getByText('R$ 600'))
    fireEvent.click(screen.getByRole('button', { name: /comecar/i }))

    expect(onComplete).toHaveBeenCalledWith({
      level: 'beginner',
      style: 'control',
      budget_max: 600,
    })

    // Also check localStorage
    const raw = localStorageMock.getItem('pickleiq:profile:myuid')
    expect(raw).not.toBeNull()
    const saved = JSON.parse(raw!)
    expect(saved.level).toBe('beginner')
    expect(saved.budget_max).toBe(600)
  })

  it('Test 7: editing profile updates localStorage without clearing external state', () => {
    localStorageMock.setItem('pickleiq:uid', 'myuid')
    saveProfile({ level: 'beginner', style: 'control', budget_max: 600 })

    const onComplete = vi.fn()
    render(React.createElement(QuizFlow, { onComplete, editMode: true }))

    // Change level to advanced
    fireEvent.click(screen.getByText('Avancado'))
    fireEvent.click(screen.getByRole('button', { name: /proximo/i }))

    fireEvent.click(screen.getByText('Potencia'))
    fireEvent.click(screen.getByRole('button', { name: /proximo/i }))

    fireEvent.click(screen.getByText('R$ 1000'))
    fireEvent.click(screen.getByRole('button', { name: /comecar/i }))

    const saved = JSON.parse(localStorageMock.getItem('pickleiq:profile:myuid')!)
    expect(saved.level).toBe('advanced')
    expect(onComplete).toHaveBeenCalledTimes(1)
  })
})

describe('Edit profile option', () => {
  it('Test 6: QuizFlow in editMode pre-fills values from existing profile', () => {
    localStorageMock.setItem('pickleiq:uid', 'myuid')
    saveProfile({ level: 'intermediate', style: 'balanced', budget_max: 800 })

    render(React.createElement(QuizFlow, { onComplete: vi.fn(), editMode: true }))
    // The quiz should still show step 1 with pre-filled selection visible
    expect(screen.getByText(/qual o seu nivel de jogo/i)).toBeDefined()
    // The advance button should be enabled because existing profile pre-fills level
    const btn = screen.getByRole('button', { name: /proximo/i })
    expect(btn).toHaveProperty('disabled', false)
  })
})
