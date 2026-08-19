# Safe Archive Candidates

> **IMPORTANT**: This document lists candidates for future archival. **No files have been moved or deleted**. Archival should only occur after explicit user approval.

## 1. Superseded Model Artifacts (ml/models/)

These 24 artifacts belong to previous training iterations and are inactive in the database (`ModelRun.is_active = False`):

| File Path | Version | Size | Reason for Archiving | Risk Level |
| :--- | :--- | :--- | :--- | :--- |
| `ml/models/catboost_h{1,2,3}_vv20260818_135151.cbm` + metadata (4 files) | `v20260818_135151` | ~417 KB | Superseded by active version `v20260818_153724` | Low |
| `ml/models/catboost_h{1,2,3}_vv20260815_172455.cbm` + metadata (4 files) | `v20260815_172455` | ~440 KB | Older training run | Low |
| `ml/models/catboost_h{1,2,3}_vv20260813_083455.cbm` + metadata (4 files) | `v20260813_083455` | ~370 KB | Older training run | Low |
| `ml/models/catboost_h{1,2,3}_vv20260813_082709.cbm` + metadata (4 files) | `v20260813_082709` | ~207 KB | Older training run | Low |
| `ml/models/catboost_h{1,2,3}_vv20260813_053513.cbm` + metadata (4 files) | `v20260813_053513` | ~308 KB | Initial baseline run | Low |
| `ml/models/catboost_h{1,2,3}_v1.1.0.cbm` + metadata (4 files) | `v1.1.0` | ~880 KB | Legacy non-versioned format | Low |

---

## 2. Duplicate / Stale Database Files

| File Path | Size | Reason for Archiving | Risk Level |
| :--- | :--- | :--- | :--- |
| `backend/cropmandi.db` | 147 KB | Stale secondary database file; primary 11.3 MB database is located at root `cropmandi.db` | Medium |

---

## 3. Unused Frontend Components

| File Path | Component Name | Reason for Archiving | Risk Level |
| :--- | :--- | :--- | :--- |
| `frontend/src/components/forecast/ForecastHistoryPanel.tsx` | `ForecastHistoryPanel` | Removed from UI in user request #5; no longer imported or rendered | Low |

---

## 4. Experimental Notebooks & Stub Scripts

| File Path | Purpose | Recommended Action | Risk Level |
| :--- | :--- | :--- | :--- |
| `cropmandi_ai_model_training.ipynb` | Initial exploratory Jupyter training notebook | Safe to archive once all feature pipelines are in python modules | Low |
| `backend/scripts/verify_real_prediction.py` | 328-byte wrapper script | Keep or archive in favor of canonical `scripts/verify_real_prediction.py` | Low |
