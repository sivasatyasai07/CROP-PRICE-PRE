from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class OfficialMarketPrice(Base):
    __tablename__ = "official_market_prices"

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(100), nullable=False, default="official_api") # official_api, official_database, official_csv
    source_record_id = Column(String(255), nullable=False, unique=True, index=True)
    market_id = Column(Integer, ForeignKey("markets.id"), nullable=False, index=True)
    commodity_id = Column(Integer, ForeignKey("commodities.id"), nullable=False, index=True)
    observation_date = Column(Date, nullable=False, index=True)
    min_price = Column(Float, nullable=True)
    modal_price = Column(Float, nullable=False)
    max_price = Column(Float, nullable=True)
    arrival_quantity = Column(Float, nullable=True)
    original_market_name = Column(String(255), nullable=True)
    original_commodity_name = Column(String(255), nullable=True)
    fetched_at = Column(DateTime, default=datetime.utcnow)
    last_verified_at = Column(DateTime, default=datetime.utcnow)
    data_status = Column(String(50), default="fresh_official") # fresh_official, cached_official
    verification_status = Column(String(50), default="verified") # verified, api_verified, database_verified
    raw_payload_hash = Column(String(255), nullable=False)
    raw_payload = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    market = relationship("Market")
    commodity = relationship("Commodity")
