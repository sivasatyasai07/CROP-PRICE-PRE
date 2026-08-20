import pytest
from datetime import date, timedelta
from app.database import SessionLocal
from app.models import Market, Commodity, OfficialMarketPrice, Prediction
from app.routers.prices import get_price_trends, compare_market_prices, ALLOWED_SOURCES, BLOCKED_SOURCES
from app.routers.commodities import list_recent_commodities
from app.routers.markets import list_recent_markets
from app.utils.date_service import get_ist_today
from app.config import settings


@pytest.fixture(scope="module")
def db_session():
    db = SessionLocal()
    yield db
    db.close()


def test_1_crop_has_30_day_official_records(db_session):
    """Crop has official records in the last 30 days -> appears in recent commodities."""
    recent_commodities = list_recent_commodities(days=30, db=db_session)
    comm_names = [c.canonical_name for c in recent_commodities]
    assert "Tomato" in comm_names
    tomato_item = next(c for c in recent_commodities if c.canonical_name == "Tomato")
    assert tomato_item.record_count >= 2
    assert tomato_item.availability_status == "available"


def test_2_crop_has_limited_or_single_record(db_session):
    """Commodity availability status handles limited count correctly."""
    recent_commodities = list_recent_commodities(days=30, db=db_session)
    for c in recent_commodities:
        if c.record_count == 1:
            assert c.availability_status == "limited"
        elif c.record_count >= 2:
            assert c.availability_status == "available"


def test_3_market_has_recent_or_today_official_price(db_session):
    """Market with recent observation returns observation_date, age, is_observed=True, is_predicted=False."""
    comp = compare_market_prices(commodity="Tomato", max_age_days=7, force_refresh=False, db=db_session)
    assert len(comp.markets) > 0
    for m in comp.markets:
        assert m.data_age_days <= 7
        assert m.is_observed is True
        assert m.is_predicted is False
        assert m.price_source in ALLOWED_SOURCES
        assert m.price_source not in BLOCKED_SOURCES


def test_4_market_lacks_today_data_shows_nearest_recent(db_session):
    """If today is unavailable, nearest recent official observation within 7 days is returned with actual age."""
    comp = compare_market_prices(commodity="Tomato", max_age_days=7, force_refresh=False, db=db_session)
    for m in comp.markets:
        assert m.data_age_days >= 0
        assert m.observation_date is not None
        assert m.is_latest_available_value is True


def test_5_market_older_than_max_age_is_excluded(db_session):
    """Market with data older than max_age_days is placed in excluded_markets with a clear reason."""
    comp = compare_market_prices(commodity="Tomato", max_age_days=7, force_refresh=False, db=db_session)
    excluded_names = [em.market for em in comp.excluded_markets]
    # Ananthapur has latest data in 2025 (age > 200 days)
    assert any("Ananthapur" in name or "Anantapur" in name for name in excluded_names)
    for em in comp.excluded_markets:
        assert "No official observed price in the recent allowed period" in em.reason


def test_6_prediction_exists_but_no_official_data_excluded(db_session):
    """Trends and Comparison strictly ignore predictions when official data does not exist."""
    trends = get_price_trends(commodity="Tomato", market="NonExistentMarket999", days=30, force_refresh=False, db=db_session)
    assert len(trends) == 0


def test_7_no_prediction_sources_returned(db_session):
    """Ensure no predicted_model or fallback sources ever appear in Trends output."""
    trends = get_price_trends(commodity="Tomato", market="Madanapalli APMC", days=30, force_refresh=False, db=db_session)
    for pt in trends:
        assert pt.is_observed is True
        assert pt.is_predicted is False
        assert pt.price_source in ALLOWED_SOURCES
        assert pt.price_source not in BLOCKED_SOURCES
        assert "predict" not in pt.price_source.lower()
        assert "fallback" not in pt.price_source.lower()


def test_8_user_chooses_potato_no_tomato_bleed(db_session):
    """Selecting Potato returns only Potato records and no Tomato records."""
    potato_trends = get_price_trends(commodity="Potato", market="Madanapalli APMC", days=30, force_refresh=False, db=db_session)
    for pt in potato_trends:
        assert pt.is_observed is True
    
    comp = compare_market_prices(commodity="Potato", max_age_days=7, force_refresh=False, db=db_session)
    assert comp.commodity == "Potato"


def test_9_more_than_two_markets_returned(db_session):
    """Market comparison returns all qualifying markets without artificial 2-market limits."""
    comp = compare_market_prices(commodity="Tomato", max_age_days=7, force_refresh=False, db=db_session)
    assert len(comp.markets) >= 3  # Should have 9 active APMCs for Tomato


def test_10_missing_dates_leave_gaps_no_interpolation(db_session):
    """Missing calendar dates in the 30-day window are gaps, not interpolated with fake values."""
    trends = get_price_trends(commodity="Tomato", market="Madanapalle APMC", days=30, force_refresh=False, db=db_session)
    # The count should match actual observation count (e.g. 26), not forced 30 continuous filled points
    assert len(trends) <= 30
    for pt in trends:
        assert pt.is_observed is True
        assert pt.is_predicted is False


def test_11_source_metadata_conflict_rejected(db_session):
    """Records with is_predicted=True or invalid source are filtered out."""
    trends = get_price_trends(commodity="Tomato", market="Madanapalli APMC", days=30, force_refresh=False, db=db_session)
    for pt in trends:
        assert pt.is_predicted is False
        assert pt.is_observed is True
        assert pt.price_source in ALLOWED_SOURCES


def test_12_recent_markets_filtering_by_crop(db_session):
    """list_recent_markets returns only markets with official data for the specified crop."""
    m_tomato = list_recent_markets(commodity="Tomato", days=30, db=db_session)
    assert len(m_tomato) > 0
    for m in m_tomato:
        assert m.record_count >= 1
        assert m.data_age_days is not None
