from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
import app.models # Ensure models are loaded

from app.routers import (
    health,
    auth,
    markets,
    commodities,
    prices,
    predictions,
    training,
    data_ingestion,
    weather,
    recommendations,
    admin,
    disease,
    forecast,
    sync
)

# Auto-create tables for SQLite / dev startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version="2.0.0",
    description="CropMandi AI – Verified 3-Day Farmer Mandi Price Prediction System API"
)

# CORS configuration
origins = settings.CORS_ORIGINS
if isinstance(origins, str):
    origins = [origins]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router)
app.include_router(auth.router)
app.include_router(markets.router)
app.include_router(commodities.router)
app.include_router(prices.router)
app.include_router(predictions.router)
app.include_router(training.router)
app.include_router(data_ingestion.router)
app.include_router(weather.router)
app.include_router(recommendations.router)
app.include_router(admin.router)
app.include_router(disease.router)
app.include_router(forecast.router)
app.include_router(sync.router, prefix="/api/v1")

@app.on_event("startup")
def startup_price_sync_event():
    from app.services.master_data_service import load_master_data
    from app.services.scheduler_service import start_background_startup_sync, start_daily_scheduler
    load_master_data()
    start_background_startup_sync()
    start_daily_scheduler()

@app.get("/")
def root():
    return {
        "message": "Welcome to CropMandi AI Backend API",
        "docs_url": "/docs",
        "health_check": "/api/v1/health"
    }
