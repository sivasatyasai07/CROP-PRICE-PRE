# Deployment Runtime & Architecture Audit Report

**Date & Time**: 2026-08-19 22:48 IST  
**Target Environment**: Render Web Service (`https://crop-price-pre-1.onrender.com`) & Static Site (`https://crop-price-pre-2.onrender.com`)

---

## 1. Executive Summary & Root Cause Analysis

### A. Root Cause of Missing Predictions ("Model artifact not loaded for version 2.1.0")
1. **Git Exclusion Bug**: `cropmandi-ai/.gitignore` explicitly contained:
   ```gitignore
   ml/models/*.cbm
   ml/models/*.pkl
   ml/models/*.json
   ```
   This prevented the trained CatBoost multi-horizon model artifacts (`catboost_h1_vv20260818_153724.cbm`, etc.) and conformal prediction metadata from ever being committed to Git or deployed to Render.
2. **Version String Mismatch**: `app/ml/predict.py` had a default hardcoded `model_version = "2.1.0"`, whereas the trained and registered database model version was `v20260818_153724`.
3. **Silent Fallback Suppression**: When the model artifact was not found, the system fell back to last-observed price with `predicted_modal_price = None` when no local database record existed, displaying "Unavailable".

### B. Root Cause of Empty / Incomplete Crops & Markets in Trends and Weather
1. **Unseeded Production Database**: On Render's ephemeral filesystem, SQLite started fresh. Commodities and APMC Markets were only created on-demand when price records arrived.
2. **Strict CleanedMarketPrice Join**: `/api/v1/commodities` and `/api/v1/markets` joined on `CleanedMarketPrice`, filtering out all commodities and markets if no recent cleaned observation existed in DB.
3. **Missing Market Coordinates**: Default unseeded markets lacked latitude/longitude, causing `WeatherTab` coordinate filter to return 0 markets.

---

## 2. Component & Architecture Inventory

| Component | Repository Path | Runtime Role | Deployed to Render | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Root Entrypoint** | `main.py` | Uvicorn wrapper (`uvicorn main:app`) | Yes | Verified |
| **Backend App Entry** | `cropmandi-ai/backend/app/main.py` | FastAPI application initialization | Yes | Verified |
| **Configuration** | `cropmandi-ai/backend/app/config.py` | Pydantic Settings & API keys | Yes | Verified |
| **Database & ORM** | `cropmandi-ai/backend/app/database.py`, `models.py` | SQLite / PostgreSQL SQLAlchemy models | Yes | Verified |
| **Seeder Service** | `cropmandi-ai/backend/app/services/seed_service.py` | Auto-seeds 30+ APMC markets & 21 crops | Yes | Added & Active |
| **Official API Sync** | `app/services/official_market_service.py` | data.gov.in exact multi-date fetcher | Yes | Active |
| **Master CSV Loader** | `app/services/master_data_service.py` | Loads `data/master-data.csv` | Yes | Active |
| **Forecast Reconciler**| `app/services/forecast_reconciliation_service.py` | 5-stage precedence reconciler | Yes | Active |
| **ML Model Registry** | `cropmandi-ai/backend/app/ml/model_registry.py` | Loads CatBoost H1/H2/H3 & metadata | Needs Artifact Tracking | Fixing |
| **ML Predictor** | `cropmandi-ai/backend/app/ml/predict.py` | Feature builder & multi-horizon inference | Yes | Fixing |
| **CatBoost Artifacts** | `cropmandi-ai/ml/models/*.cbm`, `*.pkl` | Trained H1, H2, H3 weights & metadata | Previously Ignored in Git | To Track in Git |
| **Weather Router** | `app/routers/weather.py` | Open-Meteo API proxy & APMC weather | Yes | Active |
| **Frontend UI** | `cropmandi-ai/frontend/src/` | React 18 + Vite + TypeScript SPA | Yes | Active |

---

## 3. Precedence Hierarchy for Verified Predictions

For every target date $D \in \{D_0, D_1, D_2, D_3\}$ independently:
1. **Priority 1: Official data.gov.in Live API** (`official_api` / `api_live_verified`)
2. **Priority 2: Authoritative master-data.csv** (`official_csv` / `master_csv_verified`)
3. **Priority 3: CatBoost Multi-Horizon ML Inference** (`predicted_model` / `trained_model` with 80% conformal intervals)
4. **Priority 4: Explicit Fallback (Last Observed Official Price)** (`fallback_last_observed`)
5. **Priority 5: Price Unavailable** (`unavailable`)

---

## 4. Remediation Plan

1. **Unignore Model Artifacts**: Remove `ml/models/*.cbm` and `ml/models/*.pkl` from `.gitignore` so CatBoost binaries are tracked in Git and present on Render.
2. **Implement Model Health & System Health Endpoints**:
   - `GET /api/v1/models/health`
   - `GET /api/v1/system/health`
   - `GET /api/v1/weather/coverage`
3. **Fix Dynamic Model Version Resolution**: Look up active version from `ModelRun` table, match files in `cropmandi-ai/ml/models/`, and load H1, H2, and H3 with full feature schema validation.
4. **Button State & UI**: Show `Generating...` in button, increase button size, and remove "3-Day Forecast" redundant title from button if requested.
5. **Add Verification Scripts**: Create `scripts/verify_live_forecast_deployment.py`, `scripts/verify_model_artifacts.py`, `scripts/verify_coverage.py`, `scripts/verify_api_to_prediction_flow.py`.
