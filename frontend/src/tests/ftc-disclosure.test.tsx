import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { FTCDisclosure } from '@/components/ftc-disclosure'
import { markAffiliateContent, generateBlogMetadata } from '@/lib/content'

describe('FTCDisclosure component', () => {
  it('renders badge with correct text', () => {
    render(<FTCDisclosure />)
    expect(screen.getByText(/Divulgação FTC: Links de Afiliado/i)).toBeTruthy()
  })

  it('renders "saiba mais" link pointing to #ftc-disclaimer', () => {
    render(<FTCDisclosure />)
    const link = screen.getByRole('link', { name: /saiba mais/i })
    expect(link.getAttribute('href')).toBe('#ftc-disclaimer')
  })

  it('applies yellow background class', () => {
    const { container } = render(<FTCDisclosure />)
    const badge = container.firstChild as HTMLElement
    expect(badge.className).toContain('bg-yellow-100')
  })

  it('applies yellow text class', () => {
    const { container } = render(<FTCDisclosure />)
    const badge = container.firstChild as HTMLElement
    expect(badge.className).toContain('text-yellow-900')
  })

  it('applies yellow border class', () => {
    const { container } = render(<FTCDisclosure />)
    const badge = container.firstChild as HTMLElement
    expect(badge.className).toContain('border-yellow-300')
  })

  it('is compact: uses text-xs', () => {
    const { container } = render(<FTCDisclosure />)
    const badge = container.firstChild as HTMLElement
    expect(badge.className).toContain('text-xs')
  })
})

describe('markAffiliateContent', () => {
  it('injects [FTC_DISCLOSURE] marker before first Mercado Livre URL', () => {
    const content = 'Buy here: https://mercadolivre.com/produto/123'
    const result = markAffiliateContent(content)
    expect(result).toContain('[FTC_DISCLOSURE]https://mercadolivre.com/produto/123')
  })

  it('returns content unchanged when no Mercado Livre URL present', () => {
    const content = 'No affiliate links here.'
    expect(markAffiliateContent(content)).toBe(content)
  })

  it('only injects marker before the first occurrence', () => {
    const content =
      'First: https://mercadolivre.com/a Second: https://mercadolivre.com/b'
    const result = markAffiliateContent(content)
    const count = (result.match(/\[FTC_DISCLOSURE\]/g) || []).length
    expect(count).toBe(1)
  })
})

describe('generateBlogMetadata', () => {
  it('returns object with title including site name', () => {
    const meta = generateBlogMetadata('Test Title', 'A description', 'test-slug')
    expect(meta.title).toContain('Test Title')
    expect(meta.title).toContain('PickleIQ')
  })

  it('returns canonical URL with slug', () => {
    const meta = generateBlogMetadata('Title', 'Desc', 'my-article')
    expect(meta.canonical).toBe('https://pickleiq.com/blog/my-article')
  })

  it('sets robots to index, follow', () => {
    const meta = generateBlogMetadata('Title', 'Desc', 'slug')
    expect(meta.robots).toBe('index, follow')
  })
})
