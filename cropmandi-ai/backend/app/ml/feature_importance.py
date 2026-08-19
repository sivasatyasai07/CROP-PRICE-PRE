from typing import Dict, List, Any
import numpy as np

def extract_feature_importance(model, feature_names: List[str], top_n: int = 10) -> List[Dict[str, Any]]:
    """
    Extracts top feature importance scores from CatBoost model.
    """
    try:
        raw_importances = model.get_feature_importance()
        sorted_indices = np.argsort(raw_importances)[::-1]

        results = []
        for idx in sorted_indices[:top_n]:
            results.append({
                "feature": feature_names[idx],
                "importance": round(float(raw_importances[idx]), 3)
            })
        return results
    except Exception:
        return []

def get_farmer_friendly_explanation(top_features: List[Dict[str, Any]], language: str = "en") -> List[str]:
    """
    Translates top technical features into farmer-friendly explanations.
    """
    explanations = []
    for item in top_features[:4]:
        feat = item["feature"]
        if "lag_1" in feat or "rolling_mean_3" in feat:
            explanations.append("Recent mandi modal price trend over the past few days" if language == "en" else "గత కొన్ని రోజుల మండి ధరల ధోరణి")
        elif "arrival" in feat or "pressure" in feat:
            explanations.append("Current mandi arrival volume and supply pressure" if language == "en" else "ప్రస్తుత మండి రాక పరిమాణం మరియు సరఫరా ఒత్తిడి")
        elif "seasonal" in feat or "month" in feat or "lag_365" in feat:
            explanations.append("Same-season historical price pattern from previous periods" if language == "en" else "గత కాలాల నుండి అదే సీజన్ చారిత్రక ధరల సరళి")
        elif "rainfall" in feat or "temp" in feat or "weather" in feat:
            explanations.append("Recent weather observations and precipitation levels" if language == "en" else "ఇటీవలి వాతావరణ పరిశీలనలు మరియు వర్షపాతం స్థాయిలు")
        elif "regional" in feat or "cross" in feat:
            explanations.append("Price movements in neighboring APMC yards" if language == "en" else "సమీప APMC మార్కెట్లలో ధరల కదలికలు")

    if not explanations:
        explanations.append("Recent mandi price movements and historical patterns" if language == "en" else "ఇటీవలి మండి ధరల కదలికలు మరియు చారిత్రక సరళి")

    return list(dict.fromkeys(explanations))
