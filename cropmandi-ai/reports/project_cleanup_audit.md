# CropMandi AI Read-Only Project Cleanup Audit Report

## 1. Executive Summary

This audit provides a comprehensive, read-only inventory of the CropMandi AI codebase. **No files have been modified, moved, renamed, or deleted during this audit.**

- **Active Model Version**: `v20260818_153724` (CatBoostRegressor Direct 3-Horizon, 98 canonical leak-free features).
- **Active Primary Database**: `cropmandi.db` (11.3 MB SQLite database at project root).
- **Active Master Data**: `backend/data/master-data.csv` (4.5 MB official AP mandi dataset 2021–2026).
- **Active Model Artifacts**: 4 files (`catboost_h1_vv20260818_153724.cbm`, `catboost_h2_vv20260818_153724.cbm`, `catboost_h3_vv20260818_153724.cbm`, `metadata_vv20260818_153724.pkl`).
- **Archive Candidates**: 24 superseded model files, 1 stale duplicate DB, 1 unmounted frontend component, and 1 development notebook.

---

## 2. End-to-End Runtime Pipeline Tracing

| Pipeline Stage | Active Component | Function / Export | Status |
| :--- | :--- | :--- | :--- |
| **Frontend View** | `frontend/src/components/FarmerForecastTab.tsx` | `FarmerForecastTab` | Active (On-demand trigger) |
| **Trigger Button** | `frontend/src/components/forecast/ForecastButton.tsx` | `ForecastButton` | Active |
| **Forecast Hook** | `frontend/src/hooks/useVerifiedForecast.ts` | `useVerifiedForecast()` | Active |
| **API Client** | `frontend/src/services/forecastService.ts` | `fetchVerifiedForecast()` | Active |
| **Backend Route** | `backend/app/routers/forecast.py` | `@router.get("/verified")` | Active |
| **Source Priority** | `backend/app/services/forecast_reconciliation_service.py` | `reconcile_verified_forecast()` | Active (API $\to$ CSV $\to$ ML) |
| **Master Data Fallback** | `backend/app/services/master_data_service.py` | `get_master_data_price()` | Active |
| **Dataset Generator** | `backend/app/ml/dataset_builder.py` | `build_dataset_from_db()` | Active |
| **Feature Builder** | `backend/app/ml/feature_engineering.py` | `create_features()` | Active (98 features) |
| **Model Registry** | `backend/app/ml/model_registry.py` | `load_model_artifacts()` | Active |
| **Inference Engine** | `backend/app/ml/predict.py` | `generate_3day_prediction()` | Active |
| **Interval Engine** | `backend/app/ml/prediction_intervals.py` | `apply_prediction_interval()` | Active (Conformal $q_{80}$) |
| **UI Display** | `frontend/src/components/forecast/ForecastResult.tsx` | `ForecastResult` | Active (Black typography, 3 cards) |

---

## 3. Detailed Component Inventory

### A. Active Runtime Files (MUST KEEP)
- **Backend Core**: `main.py`, `config.py`, `database.py`, `models/` (all), `routers/` (all), `services/` (all), `ml/` (all).
- **Frontend Core**: `App.tsx`, `FarmerForecastTab.tsx`, `PriceTrendsTab.tsx`, `CropDiseaseTab.tsx`, `WeatherTab.tsx`, `GovernmentSchemesTab.tsx`, `MandiMitraChatbot.tsx`, `components/forecast/` (ForecastResult, ForecastButton, ClosestMarketsSection, ForecastLoadingState, DataVerificationPanel).
- **Data & Configuration**: `cropmandi.db`, `backend/data/master-data.csv`, `ml/data/market_aliases.json`, `backend/data/users.json`.

### B. Diagnostic & Operational Tools (MUST KEEP)
- `scripts/diagnose_prediction_pipeline.py` (Full pipeline diagnostics & verification).
- `scripts/verify_real_prediction.py` (Automated genuineness & sensitivity test).
- `scripts/seed_database_daily.py` (Database populator).
- `scripts/sync_latest_data.py` (Daily agmarknet sync).
- `scripts/compare_feature_sets.py` (Feature ablation benchmark).
- `scripts/train_models.py` (Multi-horizon CatBoost model trainer).

### C. Safe Archive Candidates (Action: Archive after confirmation)
1. **Old Model Artifacts (`ml/models/`)**:
   - `catboost_h{1,2,3}_vv20260818_135151.cbm` + `metadata_vv20260818_135151.pkl`
   - `catboost_h{1,2,3}_vv20260815_172455.cbm` + `metadata_vv20260815_172455.pkl`
   - `catboost_h{1,2,3}_vv20260813_083455.cbm` + `metadata_vv20260813_083455.pkl`
   - `catboost_h{1,2,3}_vv20260813_082709.cbm` + `metadata_vv20260813_082709.pkl`
   - `catboost_h{1,2,3}_vv20260813_053513.cbm` + `metadata_vv20260813_053513.pkl`
   - `catboost_h{1,2,3}_v1.1.0.cbm` + `metadata_v1.1.0.pkl`
2. **Duplicate/Stale Database**:
   - `backend/cropmandi.db` (147 KB stale local copy; root `cropmandi.db` is 11.3 MB).
3. **Unused Frontend Component**:
   - `frontend/src/components/forecast/ForecastHistoryPanel.tsx` (Unmounted per user request #5).
4. **Notebook**:
   - `cropmandi_ai_model_training.ipynb` (Exploratory training notebook).

---

## 4. Recommended Cleanup Order (When Approved)

```text
Step 1: Backup project state.
Step 2: Create archive/ directory structure (archive/models, archive/data, archive/scripts, archive/notebooks).
Step 3: Move the 24 superseded model artifacts to archive/models/.
Step 4: Move stale backend/cropmandi.db to archive/data/.
Step 5: Move ForecastHistoryPanel.tsx and cropmandi_ai_model_training.ipynb to archive/.
Step 6: Run full backend test suite (`python -m pytest`).
Step 7: Run frontend build (`npm run build`).
Step 8: Execute `python scripts/diagnose_prediction_pipeline.py`.
```

---

## 5. Generated Inventory Reports

- [`reports/project_file_inventory.json`](file:///c:/Users/sivas/OneDrive/Desktop/ghfh/cropmandi-ai/reports/project_file_inventory.json)
- [`reports/model_artifact_inventory.json`](file:///c:/Users/sivas/OneDrive/Desktop/ghfh/cropmandi-ai/reports/model_artifact_inventory.json)
- [`reports/data_file_inventory.json`](file:///c:/Users/sivas/OneDrive/Desktop/ghfh/cropmandi-ai/reports/data_file_inventory.json)
- [`reports/runtime_dependency_graph.md`](file:///c:/Users/sivas/OneDrive/Desktop/ghfh/cropmandi-ai/reports/runtime_dependency_graph.md)
- [`reports/safe_archive_candidates.md`](file:///c:/Users/sivas/OneDrive/Desktop/ghfh/cropmandi-ai/reports/safe_archive_candidates.md)
