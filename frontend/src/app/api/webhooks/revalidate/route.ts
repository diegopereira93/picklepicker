import { revalidateWebhook } from '@/lib/revalidate'

export async function POST(req: Request) {
  return revalidateWebhook(req)
}
