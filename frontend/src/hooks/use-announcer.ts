'use client';

import { useState, useCallback } from 'react';

/**
 * useAnnouncer hook for screen reader announcements
 *
 * Use this hook to announce dynamic content changes to screen readers.
 * The announcement is polite (non-interrupting) by default.
 *
 * @example
 * const { announce, announcement } = useAnnouncer();
 *
 * // Announce when products load
 * useEffect(() => {
 *   if (products.length > 0) {
 *     announce(`${products.length} products loaded`);
 *   }
 * }, [products]);
 *
 * // Include the live region in your component
 * return (
 *   <>
 *     <Announcer announcement={announcement} />
 *     <ProductList products={products} />
 *   </>
 * );
 */
export function useAnnouncer() {
  const [announcement, setAnnouncement] = useState('');

  const announce = useCallback((message: string) => {
    setAnnouncement(message);
    // Clear after a delay to prevent duplicate announcements
    setTimeout(() => setAnnouncement(''), 1000);
  }, []);

  return { announce, announcement };
}

/**
 * Announcer component - renders an aria-live region for screen readers
 *
 * Place this component once in your app (typically in layout) or
 * use it within specific components that need announcements.
 */
interface AnnouncerProps {
  announcement: string;
  politeness?: 'polite' | 'assertive';
}

export function Announcer({ announcement, politeness = 'polite' }: AnnouncerProps) {
  return (
    <div
      aria-live={politeness}
      aria-atomic="true"
      className="sr-only"
      role="status"
    >
      {announcement}
    </div>
  );
}

/**
 * Simple announce function that creates a temporary live region
 * Useful for one-off announcements without hook state
 */
export function announceToScreenReader(message: string, politeness: 'polite' | 'assertive' = 'polite') {
  if (typeof window === 'undefined') return;

  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', politeness);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;

  document.body.appendChild(announcement);

  // Remove after announcement is read
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
}
