import { auth } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  const { userId } = await auth();

  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { paddle_id, price_target } = await req.json();

  const backendUrl = process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://localhost:8000';
  const res = await fetch(`${backendUrl}/price-alerts`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: userId, paddle_id, price_target }),
  });

  if (!res.ok) {
    return NextResponse.json({ error: 'Failed to create alert' }, { status: 500 });
  }

  const alert = await res.json();
  return NextResponse.json(alert, { status: 201 });
}
