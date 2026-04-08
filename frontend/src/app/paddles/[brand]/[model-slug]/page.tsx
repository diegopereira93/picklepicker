import { redirect } from 'next/navigation'

export const dynamic = 'force-dynamic'

export default function ProductRedirectPage({
  params,
}: {
  params: { brand: string; 'model-slug': string }
}) {
  const slug = params['model-slug']
  redirect(`/catalog/${slug}`)
}
