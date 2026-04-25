import { auth } from '@clerk/nextjs/server';
import { NextResponse } from 'next/server';

export async function POST(req: Request) {
  const { userId } = await auth();

  if (!userId) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 });
  }

  const { old_uuid } = await req.json();

  const backendUrl = process.env.FASTAPI_INTERNAL_URL || process.env.NEXT_PUBLIC_FASTAPI_URL || 'http://localhost:8000';
  const res = await fetch(`${backendUrl}/users/migrate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ old_uuid, new_user_id: userId }),
  });

  if (!res.ok) {
    return NextResponse.json({ error: 'Migration failed' }, { status: 500 });
  }

  return NextResponse.json({ success: true });
}
