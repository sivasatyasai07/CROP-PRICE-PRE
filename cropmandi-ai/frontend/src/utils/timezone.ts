/**
 * Timezone utilities for Indian Standard Time (Asia/Kolkata)
 */

export const APP_TIMEZONE = 'Asia/Kolkata';

/**
 * Returns current date in Asia/Kolkata as YYYY-MM-DD string.
 */
export function getKolkataTodayString(): string {
  const now = new Date();
  const formatter = new Intl.DateTimeFormat('en-CA', {
    timeZone: APP_TIMEZONE,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
  return formatter.format(now); // en-CA produces YYYY-MM-DD
}

/**
 * Checks if a given date string (YYYY-MM-DD) is in the future in Asia/Kolkata timezone.
 */
export function isFutureDateInKolkata(dateStr: string): boolean {
  if (!dateStr) return false;
  const todayStr = getKolkataTodayString();
  return dateStr > todayStr;
}

/**
 * Formats a date string into readable Indian format e.g. "17 Aug 2026".
 */
export function formatKolkataDate(dateStr: string): string {
  try {
    const [year, month, day] = dateStr.split('-').map(Number);
    const d = new Date(Date.UTC(year, month - 1, day));
    return d.toLocaleDateString('en-IN', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      timeZone: 'UTC',
    });
  } catch {
    return dateStr;
  }
}
