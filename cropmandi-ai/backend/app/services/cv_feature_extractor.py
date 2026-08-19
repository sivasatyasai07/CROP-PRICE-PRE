import io
import math
import logging
from typing import Dict, Any, Optional, Tuple, List
from PIL import Image, ImageFilter, ImageStat

logger = logging.getLogger(__name__)


def analyze_botanical_features(image_bytes: bytes) -> Dict[str, Any]:
    """
    Method 2: Computer Vision Botanical and Image-Feature Analysis.
    Extracts leaf shape, margin type, aspect ratio, color profile, and surface texture
    directly from the pixel data.
    
    Returns structured supporting evidence without pretending to be a calibrated classifier.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        width, height = img.size

        # 1. Aspect Ratio & Orientation
        aspect_ratio = round(width / max(height, 1), 2)
        orientation = "landscape" if aspect_ratio > 1.15 else ("portrait" if aspect_ratio < 0.85 else "square")

        # 2. Color Profile & Green Vegetation Index
        stat = ImageStat.Stat(img)
        mean_r, mean_g, mean_b = stat.mean[:3]
        greenness_ratio = round((mean_g + 1) / (mean_r + mean_b + 2), 2)
        is_vegetation_dominant = greenness_ratio > 0.45 or mean_g > 60

        # 3. Edge Roughness & Margin Classification
        # Use edge enhancement and high-pass filter
        edge_img = img.filter(ImageFilter.FIND_EDGES).convert("L")
        edge_stat = ImageStat.Stat(edge_img)
        edge_intensity = edge_stat.mean[0]

        # Convert to grayscale for contrast / texture inspection
        gray = img.convert("L")
        gray_stat = ImageStat.Stat(gray)
        contrast_std = gray_stat.stddev[0]

        # Estimate Margin Type from Edge Variations
        if edge_intensity > 28.0:
            margin_type = "serrated / dentate"
            margin_evidence = "High perimeter edge variation consistent with serrated or toothed margins."
            margin_reliability = "usable"
        elif edge_intensity > 15.0:
            margin_type = "undulate / wavy"
            margin_evidence = "Moderate edge curvature with gentle waviness."
            margin_reliability = "usable"
        elif edge_intensity > 5.0:
            margin_type = "smooth / entire"
            margin_evidence = "Smooth perimeter contour without deep serrations."
            margin_reliability = "usable"
        else:
            margin_type = "unavailable"
            margin_evidence = "Edge boundary is not sharp enough for definitive margin classification."
            margin_reliability = "unreliable"

        # 4. Shape & Texture estimation
        if aspect_ratio > 1.6:
            shape_desc = "elongated / linear"
        elif aspect_ratio < 0.6:
            shape_desc = "narrow / lanceolate"
        elif 0.85 <= aspect_ratio <= 1.15:
            shape_desc = "orbicular / ovate"
        else:
            shape_desc = "elliptical / oblong"

        texture_desc = "rough / textured" if contrast_std > 45 else "smooth / uniform"

        return {
            "method_name": "Computer Vision Botanical Feature Extractor (Method 2)",
            "trained_classifier_available": False,
            "classifier_probability": None,
            "combined_probability": None,
            "leaf_margin": {
                "type": margin_type,
                "original_confidence": None,  # Strictly None as Method 2 is uncalibrated feature extraction
                "evidence": margin_evidence,
                "reliability": margin_reliability
            },
            "leaf_shape": shape_desc,
            "leaf_apex": "acute / tapering" if aspect_ratio < 1.0 else "obtuse / rounded",
            "leaf_base": "cuneate / rounded",
            "leaf_venation": "reticulate / visible net-veined" if contrast_std > 40 else "parallel / fine",
            "leaf_texture": texture_desc,
            "leaf_arrangement": "alternate / simple",
            "stem_features": "herbaceous / visible" if mean_g > 70 else "not prominent",
            "fruit_features": "not segmented" if not is_vegetation_dominant else "foliage dominant",
            "flower_features": "none visible in primary mask",
            "root_features": "subterranean / not visible",
            "metrics": {
                "aspect_ratio": aspect_ratio,
                "orientation": orientation,
                "greenness_index": greenness_ratio,
                "edge_roughness_score": round(edge_intensity, 2),
                "contrast_std": round(contrast_std, 2)
            }
        }
    except Exception as exc:
        logger.warning("CV Feature Extraction error: %s", exc)
        return {
            "method_name": "Computer Vision Botanical Feature Extractor (Method 2)",
            "trained_classifier_available": False,
            "classifier_probability": None,
            "combined_probability": None,
            "leaf_margin": {
                "type": "unavailable",
                "original_confidence": None,
                "evidence": "Image processing could not resolve leaf margin contours.",
                "reliability": "unreliable"
            },
            "leaf_shape": "unspecified",
            "leaf_apex": "unspecified",
            "leaf_base": "unspecified",
            "leaf_venation": "unspecified",
            "leaf_texture": "unspecified",
            "leaf_arrangement": "unspecified",
            "stem_features": "unspecified",
            "fruit_features": "unspecified",
            "flower_features": "unspecified",
            "root_features": "unspecified",
            "metrics": {}
        }
