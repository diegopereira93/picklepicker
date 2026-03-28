import { auth } from '@clerk/nextjs/server';

/**
 * Returns the Clerk userId for the current request, or null if anonymous.
 */
export async function getUserId(): Promise<string | null> {
  const { userId } = await auth();
  return userId;
}

/**
 * Returns the Clerk userId or throws an Unauthorized error.
 * Use in Route Handlers that require authentication.
 */
export async function requireUserId(): Promise<string> {
  const { userId } = await auth();
  if (!userId) {
    throw new Error('Unauthorized');
  }
  return userId;
}
