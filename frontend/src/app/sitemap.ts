import { MetadataRoute } from 'next'
import { fetchPaddles } from '@/lib/api'

const BASE_URL = 'https://pickleiq.com'

export default async function sitemap(): MetadataRoute.Sitemap {
  // Fetch all paddle slugs for dynamic catalog routes
  let paddleEntries: MetadataRoute.Sitemap = []
  try {
    const data = await fetchPaddles({ limit: 500 })
    paddleEntries = data.items
      .filter((paddle) => paddle.model_slug)
      .map((paddle) => ({
        url: `${BASE_URL}/catalog/${paddle.model_slug}`,
        lastModified: new Date(),
        changeFrequency: 'weekly' as const,
        priority: 0.8,
      }))
  } catch {
    // If API fails, skip paddle entries — static routes still work
  }

  const staticEntries: MetadataRoute.Sitemap = [
    {
      url: BASE_URL,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1.0,
    },
    {
      url: `${BASE_URL}/catalog`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 0.9,
    },
    {
      url: `${BASE_URL}/quiz`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.8,
    },
    {
      url: `${BASE_URL}/chat`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.7,
    },
    {
      url: `${BASE_URL}/gift`,
      lastModified: new Date(),
      changeFrequency: 'monthly',
      priority: 0.6,
    },
    {
      url: `${BASE_URL}/compare`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.7,
    },
    {
      url: `${BASE_URL}/blog`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.5,
    },
  ]

  return [...staticEntries, ...paddleEntries]
}
