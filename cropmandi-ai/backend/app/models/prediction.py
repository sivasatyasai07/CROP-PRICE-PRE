from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    model_run_id = Column(Integer, ForeignKey("model_runs.id"), nullable=True)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False, index=True)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=False, index=True)
    
    prediction_date = Column(Date, nullable=True, index=True)
    forecast_origin_date = Column(Date, nullable=False, index=True)
    target_date = Column(Date, nullable=False, index=True)
    horizon = Column(Integer, nullable=False)  # 1, 2, 3
    
    predicted_modal_price = Column(Float, nullable=False)
    lower_bound = Column(Float, nullable=False)
    upper_bound = Column(Float, nullable=False)
    actual_modal_price = Column(Float, nullable=True)
    
    price_source = Column(String(50), default="predicted")
    prediction_status = Column(String(50), default="active", index=True)  # active, superseded_by_newer_forecast, superseded_by_official, expired, unavailable
    
    model_version = Column(String(50), default="catboost-v2")
    feature_snapshot_id = Column(String(100), nullable=True, index=True)
    
    official_record_id = Column(Integer, ForeignKey("official_market_prices.id"), nullable=True)
    superseded_by_official = Column(Boolean, default=False)
    superseded_by_prediction_id = Column(Integer, nullable=True)
    
    input_data_timestamp = Column(DateTime, nullable=True)
    weather_data_timestamp = Column(DateTime, nullable=True)
    arrival_data_timestamp = Column(DateTime, nullable=True)
    
    generated_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    model_run = relationship("ModelRun", back_populates="predictions")
    market = relationship("Market", back_populates="predictions")
    commodity = relationship("Commodity", back_populates="predictions")
    official_record = relationship("OfficialMarketPrice")
