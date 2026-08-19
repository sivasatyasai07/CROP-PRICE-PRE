from datetime import datetime, date
from typing import Optional

def parse_date(date_str: str) -> Optional[date]:
    """
    Parses dates in formats like DD-MM-YYYY, YYYY-MM-DD, DD/MM/YYYY, etc.
    """
    if not date_str:
        return None
    
    date_str = str(date_str).strip()
    
    formats = [
        "%d-%m-%Y",
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%b-%Y",
        "%Y/%m/%d"
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.date()
        except ValueError:
            continue
            
    return None

def is_future_date(d: date, reference_date: Optional[date] = None) -> bool:
    if reference_date is None:
        reference_date = date(2026, 8, 13) # Today's date setting
    return d > reference_date
