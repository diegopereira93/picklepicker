/**
 * Injects [FTC_DISCLOSURE] marker before the first Mercado Livre URL in content.
 * Only the first occurrence is marked (badge renders once above the first affiliate link).
 */
export function markAffiliateContent(content: string): string {
  const mercadoLivreRegex = /https:\/\/mercadolivre\.com/
  if (mercadoLivreRegex.test(content)) {
    return content.replace(mercadoLivreRegex, '[FTC_DISCLOSURE]$&')
  }
  return content
}

/**
 * Generates SEO metadata for blog posts.
 */
export function generateBlogMetadata(
  title: string,
  description: string,
  slug: string,
) {
  return {
    title: `${title} - PickleIQ Blog`,
    description,
    canonical: `https://pickleiq.com/blog/${slug}`,
    robots: 'index, follow',
  }
}
