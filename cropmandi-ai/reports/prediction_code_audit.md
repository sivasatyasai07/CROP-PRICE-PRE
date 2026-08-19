# Comprehensive Prediction Pipeline Code Audit Report

## 1. Execution Path Tracing & Source Audit

| Component | File Path | Primary Function / Handler | Line Numbers | Type | Validation Result |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Frontend Generate Action** | `frontend/src/components/FarmerForecastTab.tsx` | `handleGenerateForecast()` | L137–142 | Runtime UI | PASS: Triggered on user button click; no auto-fetch on mount |
| **Forecast API Client** | `frontend/src/services/forecastService.ts` | `fetchVerifiedForecast()` | L55–75 | Runtime Axios | PASS: Sends `commodity`, `market`, `selected_date`, `force_refresh` |
| **Backend Forecast Endpoint** | `backend/app/routers/forecast.py` | `verified_forecast()` | L25–42 | FastAPI Router | PASS: Delegates to `reconcile_verified_forecast()` |
| **Source Priority Resolver** | `backend/app/services/forecast_reconciliation_service.py` | `resolve_price_for_date()` | L117–360 | Priority Chain | PASS: Priority 1 (Official API) -> Priority 2 (master-data.csv) -> Priority 3 (CatBoost ML) -> Priority 4 (Fallback) |
| **Model Registry & Loader** | `backend/app/ml/model_registry.py` | `load_model_artifacts()` | L22–38 | Disk I/O | PASS: Loads `catboost_h{1,2,3}_v{version}.cbm` and metadata |
| **Inference & Execution** | `backend/app/ml/predict.py` | `generate_3day_prediction()` | L18–200 | ML Inference | PASS: Strict date filtering `<= pred_dt`, calls `model.predict(X_pred)`, validates finite numeric output, logs error on failure |
| **Feature Engineering Matrix** | `backend/app/ml/feature_engineering.py` | `create_features()`, `build_inference_features()` | L70–165 | Leak-Free Features | PASS: 98 canonical features, strictly shifted `<= t-1` |
| **Arrival Feature Builder** | `backend/app/ml/arrival_features.py` | `build_arrival_features()` | L4–65 | Quantities & Ratios | PASS: Lags 1, 2, 3, 7, 14, rolling means, arrival pressure, and imputation flags |
| **Weather Feature Builder** | `backend/app/ml/weather_features.py` | `build_weather_features()` | L17–78 | Market Weather | PASS: Precipitation, temps, rolling rain (3d, 7d, 14d, 30d), stress flags, weather missingness |
| **Cross-Market Feature Builder** | `backend/app/ml/cross_market_features.py` | `build_cross_market_features()` | L4–38 | Spatial Signals | PASS: Regional mean, median, min, max based strictly on `lag_1` |
| **Fallback Handler** | `backend/app/ml/predict.py` | `_fallback_response()` | L202–275 | Explicit Fallback | PASS: No hardcoded agricultural values; requires actual observed price or labels as `unavailable` |
| **Response Mapper & Badges** | `frontend/src/components/forecast/ForecastResult.tsx` | `ForecastResult` | L11–225 | UI Component | PASS: Pure black prices, 3 forecast cards (`Tomorrow (Day 1)`, `Day +2`, `Day +3`), `ACTUAL PRICE (RECORDED)` vs `PREDICTED PRICE (AI MODEL)` |

---

## 2. Key Bug Fixes & Improvements

1. **Date-Aware Inference Bug Fixed**:
   - Filtered dataset strictly on `observation_date <= pred_dt`.
   - Target dates calculated dynamically as `pred_dt + timedelta(days=h)`.
   - Recorded `feature_row_date` and `days_between_feature_row_and_origin`.
2. **Elimination of Silent Fallback**:
   - Model predictions now explicitly validate `raw_output`.
   - Any runtime failure logs the full stack trace and marks `prediction_executed = False`, `prediction_method = "fallback"`, `price_source = "fallback_last_observed"`.
3. **Removal of Hard-Coded Defaults**:
   - Removed `latest_price = 2000.0` default.
   - Removed fixed `±120.0` interval margin; intervals are derived dynamically from conformal calibration residuals.
   - Removed hard-coded `0.80` / `0.70` confidence values unless calibrated metadata exists.
4. **Canonical Feature Schema**:
   - Unified feature names and categorical handling across training, baselines, and runtime inference.
   - Categorical missing values filled with `"__MISSING__"`.
   - Numeric missing values filled with `0.0`.
5. **UI Updates**:
   - Removed auto-fetch on mount (page opens blank under selection until "Generate 3-Day Forecast" is clicked).
   - Removed `Day 0` box so only the 3 forecast cards are displayed.
   - All price text styled in bold black (`#000000` / `#0f172a`).
