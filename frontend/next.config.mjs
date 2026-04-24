import withBundleAnalyzer from '@next/bundle-analyzer';

/** @type {import('next').NextConfig} */
const nextConfig = {
  async redirects() {
    return [
      {
        source: '/paddles',
        destination: '/catalog',
        permanent: true,
      },
      {
        source: '/paddles/:brand/:model-slug',
        destination: '/catalog/:model-slug',
        permanent: true,
      },
    ]
  },
  images: {
    remotePatterns: [
      // PickleIQ own domain
      { protocol: 'https', hostname: 'pickleiq.com' },
      { protocol: 'https', hostname: '*.pickleiq.com' },
      // Railway backend (API images)
      { protocol: 'https', hostname: '*.railway.app' },
      // Supabase storage
      { protocol: 'https', hostname: '*.supabase.co' },
      // Brazil Pickleball Store CDN
      { protocol: 'https', hostname: 'brazilpickleballstore.com.br' },
      { protocol: 'https', hostname: '*.brazilpickleballstore.com.br' },
      // Dropshot Brasil CDN
      { protocol: 'https', hostname: 'dropshot.com.br' },
      { protocol: 'https', hostname: '*.dropshot.com.br' },
      // JOOLA / Shopify CDN
      { protocol: 'https', hostname: 'joola.com' },
      { protocol: 'https', hostname: '*.shopify.com' },
      { protocol: 'https', hostname: '*.myshopify.com' },
      // Google user content (placeholder images)
      { protocol: 'https', hostname: '*.googleusercontent.com' },
      // Local development
      { protocol: 'http', hostname: 'localhost' },
    ],
  },
};

const bundleAnalyzerConfig = withBundleAnalyzer({
  enabled: process.env.ANALYZE === 'true',
});

export default process.env.ANALYZE === 'true'
  ? bundleAnalyzerConfig(nextConfig)
  : nextConfig;
