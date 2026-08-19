from app.utils.date_service import (
    IST_TZ,
    get_ist_now,
    get_ist_today,
    parse_internal_date,
    format_api_date,
    normalize_api_date,
    add_days,
    get_date_sequence,
    get_rolling_date_range
)

# Backwards compatibility alias
parse_date_safely = normalize_api_date
