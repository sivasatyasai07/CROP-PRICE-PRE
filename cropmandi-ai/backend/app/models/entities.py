from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, Text, ForeignKey, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Market(Base):
    __tablename__ = "markets"

    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String(255), unique=True, nullable=False, index=True)
    original_name = Column(String(255), nullable=False)
    district = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False, default="Andhra Pradesh")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    coordinate_source = Column(String(100), nullable=True, default="official_registry")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    aliases = relationship("MarketAlias", back_populates="canonical_market", cascade="all, delete-orphan")
    cleaned_prices = relationship("CleanedMarketPrice", back_populates="market")
    weather_observations = relationship("WeatherObservation", back_populates="market")
    predictions = relationship("Prediction", back_populates="market")


class Commodity(Base):
    __tablename__ = "commodities"

    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String(255), unique=True, nullable=False, index=True)
    original_name = Column(String(255), nullable=False)
    commodity_group = Column(String(100), default="Vegetables")
    unit = Column(String(50), default="₹ per quintal")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cleaned_prices = relationship("CleanedMarketPrice", back_populates="commodity")
    predictions = relationship("Prediction", back_populates="commodity")


class MarketAlias(Base):
    __tablename__ = "market_aliases"

    id = Column(Integer, primary_key=True, index=True)
    original_name = Column(String(255), unique=True, nullable=False, index=True)
    canonical_market_id = Column(Integer, ForeignKey("markets.id"), nullable=False)
    confidence = Column(Float, default=1.0)
    approved_by_user = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    canonical_market = relationship("Market", back_populates="aliases")


class RawMarketPrice(Base):
    __tablename__ = "raw_market_prices"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False)  # csv_upload, data_gov_api
    source_record_id = Column(String(255), nullable=True)
    state = Column(String(100), nullable=True)
    district = Column(String(100), nullable=True)
    original_market = Column(String(255), nullable=True)
    original_commodity = Column(String(255), nullable=True)
    commodity_group = Column(String(100), nullable=True)
    observation_date = Column(String(50), nullable=True)  # string representation before parsing
    arrival_quantity_raw = Column(String(100), nullable=True)
    min_price_raw = Column(String(100), nullable=True)
    modal_price_raw = Column(String(100), nullable=True)
    max_price_raw = Column(String(100), nullable=True)
    raw_payload = Column(Text, nullable=True)
    imported_at = Column(DateTime, default=datetime.utcnow)


class CleanedMarketPrice(Base):
    __tablename__ = "cleaned_market_prices"

    id = Column(Integer, primary_key=True, index=True)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False, index=True)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=False, index=True)
    observation_date = Column(Date, nullable=False, index=True)
    arrival_quantity = Column(Float, nullable=True)
    min_price = Column(Float, nullable=True)
    modal_price = Column(Float, nullable=False)
    max_price = Column(Float, nullable=True)
    unit = Column(String(50), default="₹ per quintal")
    arrival_missing = Column(Boolean, default=False)
    price_missing = Column(Boolean, default=False)
    suspicious_record = Column(Boolean, default=False)
    quality_status = Column(String(50), default="valid")  # valid, suspicious, warning
    source_raw_id = Column(Integer, ForeignKey("raw_market_prices.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    market = relationship("Market", back_populates="cleaned_prices")
    commodity = relationship("Commodity", back_populates="cleaned_prices")

    __table_args__ = (
        UniqueConstraint("market_id", "commodity_id", "observation_date", name="uix_market_commodity_date"),
    )


class WeatherObservation(Base):
    __tablename__ = "weather_observations"

    id = Column(Integer, primary_key=True, index=True)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False, index=True)
    observation_date = Column(Date, nullable=False, index=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    temperature_max = Column(Float, nullable=True)
    temperature_min = Column(Float, nullable=True)
    precipitation = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    wind_speed = Column(Float, nullable=True)
    weather_code = Column(Integer, nullable=True)
    weather_source = Column(String(100), default="open_meteo")
    is_historical = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    market = relationship("Market", back_populates="weather_observations")

    __table_args__ = (
        UniqueConstraint("market_id", "observation_date", name="uix_market_weather_date"),
    )


class ModelRun(Base):
    __tablename__ = "model_runs"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)  # catboost, lightgbm, baseline
    model_version = Column(String(50), nullable=False)
    training_start_date = Column(Date, nullable=True)
    training_end_date = Column(Date, nullable=True)
    validation_start_date = Column(Date, nullable=True)
    validation_end_date = Column(Date, nullable=True)
    test_start_date = Column(Date, nullable=True)
    test_end_date = Column(Date, nullable=True)
    feature_version = Column(String(50), default="v1")
    target_column = Column(String(50), default="modal_price")
    training_rows = Column(Integer, default=0)
    metrics_json = Column(JSON, nullable=True)
    artifact_path = Column(String(500), nullable=True)
    status = Column(String(50), default="completed")  # completed, failed, active
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    predictions = relationship("Prediction", back_populates="model_run")


class DataQualityReport(Base):
    __tablename__ = "data_quality_reports"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), nullable=True)
    source = Column(String(100), default="csv_upload")
    report_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DiseasePrediction(Base):
    __tablename__ = "disease_predictions"

    id = Column(String(50), primary_key=True, index=True)  # UUID string
    user_id = Column(String(100), nullable=True, index=True)
    crop = Column(String(100), nullable=False)
    disease = Column(String(255), nullable=False)
    confidence = Column(Float, nullable=False)
    result_json = Column(JSON, nullable=False)
    image_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


from app.models.official_market_price import OfficialMarketPrice
from app.models.prediction import Prediction



