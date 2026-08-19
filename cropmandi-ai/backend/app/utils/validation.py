import re
from typing import Tuple, Optional

def clean_numeric(val: any) -> Optional[float]:
    if val is None or val == "":
        return None
    val_str = str(val).strip()
    # Remove currency symbols, commas, whitespace
    cleaned = re.sub(r"[^\d.]", "", val_str)
    if not cleaned:
        return None
    try:
        res = float(cleaned)
        return res
    except ValueError:
        return None

def validate_price_relationship(min_price: Optional[float], modal_price: Optional[float], max_price: Optional[float]) -> Tuple[bool, str]:
    """
    Validates min_price <= modal_price <= max_price.
    Returns (is_valid, warning_reason).
    """
    if modal_price is None or modal_price <= 0:
        return False, "Zero or negative modal price"
    
    if min_price is not None and min_price > modal_price:
        return False, f"min_price ({min_price}) > modal_price ({modal_price})"
        
    if max_price is not None and max_price < modal_price:
        return False, f"max_price ({max_price}) < modal_price ({modal_price})"
        
    if min_price is not None and max_price is not None and min_price > max_price:
        return False, f"min_price ({min_price}) > max_price ({max_price})"

    return True, "valid"
