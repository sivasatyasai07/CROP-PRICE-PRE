import math
from sqlalchemy.orm import Session
from app.models import Market, Commodity
from app.ml.predict import generate_3day_prediction
from typing import List, Dict, Any, Optional

def compute_haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 1)

def recommend_best_markets(
    db: Session,
    commodity_name: str,
    prediction_date_str: str = "2026-08-13",
    farmer_lat: Optional[float] = None,
    farmer_lon: Optional[float] = None,
    crop_quantity_qtl: Optional[float] = None,
    transport_cost_per_km: Optional[float] = None,
    commission_pct: Optional[float] = 0.0,
    wastage_pct: Optional[float] = 0.0
) -> Dict[str, Any]:
    active_markets = db.query(Market).filter(Market.is_active == True).all()
    recommendations = []

    # Build dataset once to optimize performance across all active markets
    from app.ml.dataset_builder import build_dataset_from_db
    df_all = build_dataset_from_db(db)

    for mkt in active_markets:
        pred_res = generate_3day_prediction(db, commodity_name, mkt.canonical_name, prediction_date_str, df_all=df_all)
        # Skip markets with no real data or no predictions
        if pred_res.get("fallback_used") or not pred_res.get("predictions") or len(pred_res["predictions"]) < 3:
            continue

        h1_pred = pred_res["predictions"][0]["predicted_modal_price"]
        h3_pred = pred_res["predictions"][2]["predicted_modal_price"]

        dist_km = None
        if farmer_lat and farmer_lon and mkt.latitude and mkt.longitude:
            dist_km = compute_haversine_distance(farmer_lat, farmer_lon, mkt.latitude, mkt.longitude)

        # Net realization calculation if quantity & costs supplied
        net_realization = None
        cost_breakdown = None

        if crop_quantity_qtl and crop_quantity_qtl > 0:
            gross = h1_pred * crop_quantity_qtl
            comm_cost = gross * ((commission_pct or 0.0) / 100.0)
            wastage_cost = gross * ((wastage_pct or 0.0) / 100.0)
            trans_cost = (dist_km or 20.0) * (transport_cost_per_km or 15.0) if dist_km else 500.0
            
            net_realization = round(gross - comm_cost - wastage_cost - trans_cost, 2)
            cost_breakdown = {
                "gross_revenue": round(gross, 2),
                "commission_cost": round(comm_cost, 2),
                "wastage_cost": round(wastage_cost, 2),
                "transport_cost": round(trans_cost, 2),
                "net_realization": net_realization
            }

        recommendations.append({
            "market_id": mkt.id,
            "market_name": mkt.canonical_name,
            "district": mkt.district,
            "day1_predicted_price": h1_pred,
            "day3_predicted_price": h3_pred,
            "latest_observed_price": pred_res.get("latest_observed_price"),
            "latest_date": pred_res.get("latest_observed_date"),
            "distance_km": dist_km,
            "trend_direction": pred_res.get("trend_direction"),
            "confidence_level": pred_res["predictions"][0]["confidence_level"],
            "net_realization": net_realization,
            "cost_breakdown": cost_breakdown
        })

    # Rank by net realization if available, else by day 1 predicted price
    if crop_quantity_qtl:
        recommendations.sort(key=lambda x: x.get("net_realization") or 0, reverse=True)
        mode = "Estimated Net Realization"
    else:
        recommendations.sort(key=lambda x: x["day1_predicted_price"], reverse=True)
        mode = "Highest Predicted Mandi Price"

    return {
        "commodity": commodity_name,
        "prediction_date": prediction_date_str,
        "ranking_mode": mode,
        "notice": "Highest predicted mandi price, not guaranteed highest profit." if not crop_quantity_qtl else "Estimated net realization based on user provided costs.",
        "markets": recommendations
    }
