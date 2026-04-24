'use client';

import { useState, useCallback } from 'react';

export function useAnnouncer() {
  const [announcement, setAnnouncement] = useState('');

  const announce = useCallback((message: string) => {
    setAnnouncement(message);
    setTimeout(() => setAnnouncement(''), 1000);
  }, []);

  return { announce, announcement };
}

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

export function announceToScreenReader(message: string, politeness: 'polite' | 'assertive' = 'polite') {
  if (typeof window === 'undefined') return;

  const el = document.createElement('div');
  el.setAttribute('role', 'status');
  el.setAttribute('aria-live', politeness);
  el.setAttribute('aria-atomic', 'true');
  el.className = 'sr-only';
  el.textContent = message;
  document.body.appendChild(el);

  setTimeout(() => {
    document.body.removeChild(el);
  }, 1000);
}
