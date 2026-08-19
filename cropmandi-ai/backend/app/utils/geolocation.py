import math
from typing import List, Dict, Any, Optional, Tuple

EARTH_RADIUS_KM = 6371.0

def validate_coordinates(latitude: Optional[float], longitude: Optional[float]) -> bool:
    """
    Validates latitude and longitude coordinates.
    Rejects None, 0.0 (null island), and out-of-bound coordinates.
    """
    if latitude is None or longitude is None:
        return False
    try:
        lat = float(latitude)
        lon = float(longitude)
    except (ValueError, TypeError):
        return False

    # Check for invalid zero coordinates
    if lat == 0.0 and lon == 0.0:
        return False

    # Check valid latitude range (-90 to +90) and longitude range (-180 to +180)
    if not (-90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0):
        return False

    return True


def haversine_distance_km(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    r: float = EARTH_RADIUS_KM
) -> float:
    """
    Calculates great-circle distance between two coordinate pairs on a sphere using the Haversine formula.
    distance = 2 * R * arcsin(sqrt(sin²(Δlat/2) + cos(lat1)*cos(lat2)*sin²(Δlon/2)))
    """
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)

    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad

    a = (math.sin(dlat / 2.0) ** 2) + math.cos(lat1_rad) * math.cos(lat2_rad) * (math.sin(dlon / 2.0) ** 2)
    c = 2.0 * math.asin(math.sqrt(min(1.0, max(0.0, a))))

    return round(r * c, 2)


def calculate_market_distances(
    user_lat: float,
    user_lon: float,
    markets: List[Any]
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Calculates distances from user location to each market.
    Returns:
      (valid_market_items, markets_without_coordinates_count)
    """
    valid_items: List[Dict[str, Any]] = []
    missing_coords_count = 0

    for m in markets:
        m_id = getattr(m, "id", None)
        m_name = getattr(m, "canonical_name", None) or getattr(m, "original_name", "")
        m_district = getattr(m, "district", "")
        m_state = getattr(m, "state", "Andhra Pradesh")
        m_lat = getattr(m, "latitude", None)
        m_lon = getattr(m, "longitude", None)

        if not validate_coordinates(m_lat, m_lon):
            missing_coords_count += 1
            continue

        dist_km = haversine_distance_km(user_lat, user_lon, float(m_lat), float(m_lon))
        valid_items.append({
            "market_id": m_id,
            "market_name": m_name,
            "district": m_district,
            "state": m_state,
            "latitude": float(m_lat),
            "longitude": float(m_lon),
            "distance_km": dist_km,
        })

    return valid_items, missing_coords_count


def sort_markets_by_distance(
    market_distances: List[Dict[str, Any]],
    limit: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Sorts market items ascending by distance_km and assigns rank (1-indexed).
    """
    sorted_items = sorted(market_distances, key=lambda item: (item.get("distance_km", float("inf")), item.get("market_name", "")))

    for idx, item in enumerate(sorted_items):
        item["rank"] = idx + 1

    if limit is not None and limit > 0:
        return sorted_items[:limit]
    return sorted_items
