/**
 * blog-metadata.test.ts
 * RED phase: tests written before implementation
 * Tests pillar page content structure, FTC badge, ISR config, and metadata
 */
import { describe, it, expect } from 'vitest'
import { readFileSync } from 'fs'
import { join } from 'path'

const PILLAR_PAGE_PATH = join(__dirname, '../src/app/blog/pillar-page/page.tsx')
const BLOG_LAYOUT_PATH = join(__dirname, '../src/app/blog/layout.tsx')

function readSource(filePath: string): string {
  try {
    return readFileSync(filePath, 'utf-8')
  } catch {
    return ''
  }
}

describe('blog-metadata: pillar page structure', () => {
  it('pillar page file exists', () => {
    const src = readSource(PILLAR_PAGE_PATH)
    expect(src.length).toBeGreaterThan(0)
  })

  it('pillar page exports default function (renders without errors)', () => {
    const src = readSource(PILLAR_PAGE_PATH)
    expect(src).toMatch(/export default function/)
  })

  it('FTC badge component is imported and used', () => {
    const src = readSource(PILLAR_PAGE_PATH)
    expect(src).toMatch(/FTCDisclosure/)
  })

  it('links to at least 3 product pages (/paddles/...)', () => {
    const src = readSource(PILLAR_PAGE_PATH)
    const matches = src.match(/href=["']\/paddles\//g) || []
    expect(matches.length).toBeGreaterThanOrEqual(3)
  })

  it('ISR revalidate set to 86400 (24h)', () => {
    const src = readSource(PILLAR_PAGE_PATH)
    expect(src).toMatch(/revalidate\s*=\s*86400/)
  })

  it('generateMetadata function present', () => {
    const src = readSource(PILLAR_PAGE_PATH)
    expect(src).toMatch(/generateMetadata/)
  })

  it('metadata includes target keywords', () => {
    const src = readSource(PILLAR_PAGE_PATH)
    expect(src.toLowerCase()).toMatch(/melhor raquete/)
    expect(src.toLowerCase()).toMatch(/iniciante/)
    expect(src.toLowerCase()).toMatch(/pickleball/)
  })

  it('openGraph type article is set', () => {
    const src = readSource(PILLAR_PAGE_PATH)
    expect(src).toMatch(/type.*article/)
  })

  it('content is substantial (3000+ chars approximation)', () => {
    const src = readSource(PILLAR_PAGE_PATH)
    // The rendered text content should be significant; source > 5000 chars is a proxy
    expect(src.length).toBeGreaterThan(5000)
  })
})

describe('blog-metadata: blog layout structure', () => {
  it('blog layout file exists', () => {
    const src = readSource(BLOG_LAYOUT_PATH)
    expect(src.length).toBeGreaterThan(0)
  })

  it('blog layout has id="ftc-disclaimer" section', () => {
    const src = readSource(BLOG_LAYOUT_PATH)
    expect(src).toMatch(/id=["']ftc-disclaimer["']/)
  })

  it('blog layout exports default function', () => {
    const src = readSource(BLOG_LAYOUT_PATH)
    expect(src).toMatch(/export default function/)
  })

  it('blog layout has robots index follow metadata', () => {
    const src = readSource(BLOG_LAYOUT_PATH)
    expect(src).toMatch(/index.*follow|follow.*index/)
  })
})
