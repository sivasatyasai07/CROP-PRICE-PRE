import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal
from app.models import Market
from app.utils.geolocation import (
    haversine_distance_km,
    validate_coordinates,
    calculate_market_distances,
    sort_markets_by_distance
)

client = TestClient(app)

def test_haversine_distance_calculation():
    # Madanapalli APMC (13.5500, 78.5000) to Punganur APMC (13.3667, 78.5833)
    dist = haversine_distance_km(13.5500, 78.5000, 13.3667, 78.5833)
    assert 20.0 < dist < 30.0
    assert isinstance(dist, float)

def test_coordinate_validation():
    assert validate_coordinates(13.55, 78.50) is True
    assert validate_coordinates(0.0, 0.0) is False
    assert validate_coordinates(None, 78.50) is False
    assert validate_coordinates(13.55, None) is False
    assert validate_coordinates(95.0, 78.50) is False  # Lat > 90
    assert validate_coordinates(13.55, 190.0) is False # Lon > 180

def test_calculate_and_sort_market_distances():
    test_markets = [
        Market(id=1, canonical_name="Far APMC", latitude=17.0, longitude=82.0, district="East Godavari", is_active=True),
        Market(id=2, canonical_name="Near APMC", latitude=13.6, longitude=78.5, district="Annamayya", is_active=True),
        Market(id=3, canonical_name="No Coords APMC", latitude=None, longitude=None, district="Unknown", is_active=True),
        Market(id=4, canonical_name="Zero Coords APMC", latitude=0.0, longitude=0.0, district="Unknown", is_active=True),
    ]

    valid_items, missing_count = calculate_market_distances(13.55, 78.50, test_markets)
    assert len(valid_items) == 2
    assert missing_count == 2

    sorted_markets = sort_markets_by_distance(valid_items)
    assert sorted_markets[0]["market_name"] == "Near APMC"
    assert sorted_markets[0]["rank"] == 1
    assert sorted_markets[1]["market_name"] == "Far APMC"
    assert sorted_markets[1]["rank"] == 2

def test_closest_markets_api_endpoint():
    # User in Tirupati (13.6288, 79.4192)
    response = client.get("/api/v1/markets/closest?latitude=13.6288&longitude=79.4192&limit=5")
    assert response.status_code == 200
    data = response.json()
    assert "user_location" in data
    assert data["user_location"]["latitude"] == 13.6288
    assert data["user_location"]["longitude"] == 79.4192
    assert "markets" in data
    assert len(data["markets"]) <= 5
    assert data["total_markets_considered"] >= 12
    assert "markets_without_coordinates" in data

    # Verify ranks are ordered ascending by distance
    distances = [m["distance_km"] for m in data["markets"]]
    assert distances == sorted(distances)

def test_closest_markets_invalid_coordinates():
    response = client.get("/api/v1/markets/closest?latitude=999&longitude=79.4192")
    assert response.status_code == 400
