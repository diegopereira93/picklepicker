import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { FilterBar } from '@/components/catalog/filter-bar'
import { SelectionBar } from '@/components/catalog/selection-bar'
import { SuggestedQuestions } from '@/components/chat/suggested-questions'
import { TipCard } from '@/components/chat/tip-card'

describe('FilterBar', () => {
  const defaultProps = {
    brands: ['Nox', 'Selkirk', 'Head'],
    levels: ['beginner', 'intermediate', 'advanced'],
    activeBrand: null as string | null,
    activeLevel: null as string | null,
    resultCount: 15,
    viewMode: 'grid' as const,
    sortBy: 'name',
    onBrandChange: vi.fn(),
    onLevelChange: vi.fn(),
    onViewModeChange: vi.fn(),
    onSortChange: vi.fn(),
  }

  it('renders with brands', () => {
    render(<FilterBar {...defaultProps} />)

    // Check "Todos" button is present
    expect(screen.getByText('Todos')).toBeInTheDocument()

    // Check brand buttons are rendered
    expect(screen.getByText('Nox')).toBeInTheDocument()
    expect(screen.getByText('Selkirk')).toBeInTheDocument()
    expect(screen.getByText('Head')).toBeInTheDocument()
  })

  it('renders level chips', () => {
    render(<FilterBar {...defaultProps} />)

    // Level labels should be rendered in Portuguese
    expect(screen.getByText('Iniciante')).toBeInTheDocument()
    expect(screen.getByText('Intermediário')).toBeInTheDocument()
    expect(screen.getByText('Avançado')).toBeInTheDocument()
  })

  it('calls onBrandChange on click', () => {
    const onBrandChange = vi.fn()
    render(<FilterBar {...defaultProps} onBrandChange={onBrandChange} />)

    const brandButton = screen.getByText('Nox')
    fireEvent.click(brandButton)

    expect(onBrandChange).toHaveBeenCalledWith('Nox')
  })

  it('shows result count', () => {
    render(<FilterBar {...defaultProps} resultCount={15} />)

    expect(screen.getByText('15 raquetes encontradas')).toBeInTheDocument()
  })

  it('toggles brand off when clicking active brand', () => {
    const onBrandChange = vi.fn()
    render(
      <FilterBar {...defaultProps} activeBrand="Nox" onBrandChange={onBrandChange} />
    )

    const brandButton = screen.getByText('Nox')
    fireEvent.click(brandButton)

    expect(onBrandChange).toHaveBeenCalledWith(null)
  })
})

describe('SelectionBar', () => {
  it('returns null when count is 0', () => {
    const { container } = render(
      <SelectionBar count={0} onCompare={vi.fn()} onClear={vi.fn()} />
    )

    expect(container.firstChild).toBeNull()
  })

  it('renders when count > 0', () => {
    render(<SelectionBar count={2} onCompare={vi.fn()} onClear={vi.fn()} />)

    expect(screen.getByText('2 raquetes selecionadas')).toBeInTheDocument()
  })

  it('renders singular form when count is 1', () => {
    render(<SelectionBar count={1} onCompare={vi.fn()} onClear={vi.fn()} />)

    expect(screen.getByText('1 raquete selecionada')).toBeInTheDocument()
  })

  it('calls onClear when clear button is clicked', () => {
    const onClear = vi.fn()
    render(<SelectionBar count={2} onCompare={vi.fn()} onClear={onClear} />)

    const clearButton = screen.getByText('Limpar')
    fireEvent.click(clearButton)

    expect(onClear).toHaveBeenCalledTimes(1)
  })

  it('calls onCompare when compare button is clicked', () => {
    const onCompare = vi.fn()
    render(<SelectionBar count={2} onCompare={onCompare} onClear={vi.fn()} />)

    const compareButton = screen.getByText('Comparar')
    fireEvent.click(compareButton)

    expect(onCompare).toHaveBeenCalledTimes(1)
  })
})

describe('SuggestedQuestions', () => {
  it('returns null when empty', () => {
    const { container } = render(
      <SuggestedQuestions questions={[]} onSelect={vi.fn()} />
    )

    expect(container.firstChild).toBeNull()
  })

  it('renders questions as buttons', () => {
    const questions = [
      'Qual raquete para iniciantes?',
      'Qual a diferença entre core 14mm e 16mm?',
      'Qual raquete tem melhor controle?',
    ]

    render(<SuggestedQuestions questions={questions} onSelect={vi.fn()} />)

    questions.forEach((question) => {
      expect(screen.getByText(question)).toBeInTheDocument()
    })

    // Verify they are rendered as buttons
    const buttons = screen.getAllByRole('button')
    expect(buttons).toHaveLength(questions.length)
  })

  it('calls onSelect when button is clicked', () => {
    const onSelect = vi.fn()
    const questions = ['Qual raquete para iniciantes?']

    render(<SuggestedQuestions questions={questions} onSelect={onSelect} />)

    const button = screen.getByText('Qual raquete para iniciantes?')
    fireEvent.click(button)

    expect(onSelect).toHaveBeenCalledWith('Qual raquete para iniciantes?')
  })

  it('respects disabled prop', () => {
    const onSelect = vi.fn()
    const questions = ['Qual raquete para iniciantes?']

    render(
      <SuggestedQuestions questions={questions} onSelect={onSelect} disabled />
    )

    const button = screen.getByText('Qual raquete para iniciantes?')
    expect(button).toBeDisabled()

    fireEvent.click(button)
    expect(onSelect).not.toHaveBeenCalled()
  })
})

describe('TipCard', () => {
  it('renders content text', () => {
    const content = 'Dica: Raquetes com core 16mm oferecem mais controle.'
    render(<TipCard content={content} />)

    expect(screen.getByText(content)).toBeInTheDocument()
  })

  it('applies design-token classes', () => {
    const content = 'Test tip content'
    const { container } = render(<TipCard content={content} />)

    const cardDiv = container.firstChild as HTMLElement
    expect(cardDiv.classList.contains('mt-2')).toBe(true)
    expect(cardDiv.classList.contains('border-l-2')).toBe(true)
  })
})
