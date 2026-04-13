import { describe, it, expect, beforeEach, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import React from 'react'
import { getOrCreateUserId, getProfile, saveProfile } from '@/lib/profile'
import { QuizWidget } from '@/components/quiz/quiz-widget'

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
  it('generates UUID on first call', () => {
    const uid = getOrCreateUserId()
    expect(uid).toBe('test-uuid-1234')
    expect(localStorageMock.getItem('pickleiq:uid')).toBe('test-uuid-1234')
  })

  it('returns same UUID on subsequent calls', () => {
    localStorageMock.setItem('pickleiq:uid', 'existing-uuid')
    const uid = getOrCreateUserId()
    expect(uid).toBe('existing-uuid')
  })
})

describe('getProfile / saveProfile', () => {
  it('saves profile to localStorage under pickleiq:profile:{uid}', async () => {
    localStorageMock.setItem('pickleiq:uid', 'myuid')
    await saveProfile({ level: 'beginner', style: 'control', budget_max: 600 })
    const raw = localStorageMock.getItem('pickleiq:profile:myuid')
    expect(raw).not.toBeNull()
    const parsed = JSON.parse(raw!)
    expect(parsed).toEqual({ level: 'beginner', style: 'control', budget_max: 600 })
  })

  it('returns null when no profile stored', async () => {
    localStorageMock.setItem('pickleiq:uid', 'myuid')
    const profile = await getProfile()
    expect(profile).toBeNull()
  })

  it('returns stored profile', async () => {
    localStorageMock.setItem('pickleiq:uid', 'myuid')
    await saveProfile({ level: 'advanced', style: 'power', budget_max: 1000 })
    const profile = await getProfile()
    expect(profile?.level).toBe('advanced')
    expect(profile?.budget_max).toBe(1000)
  })
})

describe('QuizWidget component', () => {
  function renderQuiz(onComplete = vi.fn()) {
    localStorageMock.setItem('pickleiq:uid', 'myuid')
    return render(React.createElement(QuizWidget, { onComplete }))
  }

  function getSubmitButton(): HTMLElement | undefined {
    const buttons = screen.getAllByRole('button')
    return buttons.find(btn => (btn.textContent || '').includes('Comecar'))
  }

  it('renders all three sections: level, budget, style', () => {
    renderQuiz()
    expect(screen.getByText('Iniciante')).toBeDefined()
    expect(screen.getByText('Ate R$300')).toBeDefined()
    expect(screen.getByText('R$300-600')).toBeDefined()
    expect(screen.getByText('Acima R$600')).toBeDefined()
    expect(screen.getByText('Controle')).toBeDefined()
  })

  it('submit button is disabled without all selections', () => {
    renderQuiz()
    const submitBtn = getSubmitButton()
    expect(submitBtn).toBeDefined()
    expect(submitBtn!.hasAttribute('disabled')).toBe(true)
  })

  it('selecting all three options enables button', () => {
    renderQuiz()
    fireEvent.click(screen.getByText('Iniciante'))
    fireEvent.click(screen.getByText('Ate R$300'))
    fireEvent.click(screen.getByText('Controle'))
    const submitBtn = getSubmitButton()
    expect(submitBtn!.hasAttribute('disabled')).toBe(false)
  })

  it('clicking submit with all selections calls onComplete with correct profile', async () => {
    const onComplete = vi.fn()
    renderQuiz(onComplete)

    fireEvent.click(screen.getByText('Iniciante'))
    fireEvent.click(screen.getByText('Ate R$300'))
    fireEvent.click(screen.getByText('Controle'))

    const submitBtn = getSubmitButton()
    expect(submitBtn).toBeDefined()
    fireEvent.click(submitBtn!)

    await vi.waitFor(() => {
      expect(onComplete).toHaveBeenCalledWith({
        level: 'beginner',
        style: 'control',
        budget_max: 300,
      })
    })
  })

  it('saves profile to localStorage on complete', async () => {
    const onComplete = vi.fn()
    renderQuiz(onComplete)

    fireEvent.click(screen.getByText('Iniciante'))
    fireEvent.click(screen.getByText('R$300-600'))
    fireEvent.click(screen.getByText('Potencia'))

    const submitBtn = getSubmitButton()
    expect(submitBtn).toBeDefined()
    fireEvent.click(submitBtn!)

    await vi.waitFor(() => {
      const raw = localStorageMock.getItem('pickleiq:profile:myuid')
      expect(raw).not.toBeNull()
      const saved = JSON.parse(raw!)
      expect(saved.level).toBe('beginner')
      expect(saved.style).toBe('power')
      expect(saved.budget_max).toBe(600)
    })
  })
})
