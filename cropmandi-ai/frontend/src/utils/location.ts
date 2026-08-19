export interface UserLocation {
  latitude: number;
  longitude: number;
  city?: string;
  district?: string;
  state?: string;
}

export interface MandiDistance {
  market_id: number;
  market_name: string;
  district: string;
  distance_km: number;
  latitude: number;
  longitude: number;
}

/**
 * Calculate Haversine distance in km between two lat/lon coordinates
 */
export function calculateHaversineDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371; // Earth's radius in km
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return Math.round(R * c * 10) / 10; // Round to 1 decimal place
}

/**
 * Fetch reverse geocoded city name from Open-Meteo or BigDataCloud free API
 */
export async function reverseGeocode(lat: number, lon: number): Promise<{ city: string; state: string }> {
  try {
    const res = await fetch(`https://api.bigdatacloud.net/data/reverse-geocode-client?latitude=${lat}&longitude=${lon}&localityLanguage=en`);
    if (res.ok) {
      const data = await res.json();
      const city = data.locality || data.city || data.principalSubdivision || 'Detected Region';
      const state = data.principalSubdivision || 'Andhra Pradesh';
      return { city, state };
    }
  } catch (e) {
    console.warn('Reverse geocode fetch error:', e);
  }
  return { city: `${lat.toFixed(2)}°N, ${lon.toFixed(2)}°E`, state: 'Andhra Pradesh' };
}

/**
 * Get nearest AP Mandi from list of active markets
 */
export function findNearestMandi(
  userLat: number,
  userLon: number,
  markets: Array<{ id: number; canonical_name: string; district: string; latitude?: number; longitude?: number }>
): MandiDistance | null {
  if (!markets || markets.length === 0) return null;

  let nearest: MandiDistance | null = null;
  let minDistance = Infinity;

  for (const m of markets) {
    if (m.latitude && m.longitude) {
      const dist = calculateHaversineDistance(userLat, userLon, m.latitude, m.longitude);
      if (dist < minDistance) {
        minDistance = dist;
        nearest = {
          market_id: m.id,
          market_name: m.canonical_name,
          district: m.district,
          distance_km: dist,
          latitude: m.latitude,
          longitude: m.longitude,
        };
      }
    }
  }

  return nearest;
}
