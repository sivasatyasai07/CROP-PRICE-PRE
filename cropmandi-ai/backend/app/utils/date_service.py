import datetime
from typing import Optional, List, Tuple, Any
import zoneinfo

IST_TZ = zoneinfo.ZoneInfo("Asia/Kolkata")


def get_ist_now() -> datetime.datetime:
    """Return timezone-aware current datetime in Asia/Kolkata (IST)."""
    return datetime.datetime.now(IST_TZ)


def get_ist_today() -> datetime.date:
    """Return current date in Asia/Kolkata (IST)."""
    return get_ist_now().date()


def parse_internal_date(date_str: Any) -> Optional[datetime.date]:
    """
    Parses internal ISO date format YYYY-MM-DD or standard date object.
    """
    if isinstance(date_str, datetime.date):
        return date_str
    if isinstance(date_str, datetime.datetime):
        return date_str.date()
    if isinstance(date_str, str):
        date_str = date_str.strip()
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
    return None


def format_api_date(d: datetime.date) -> str:
    """
    Formats internal datetime.date into the exact DD/MM/YYYY string required by data.gov.in filters.
    Example: 2026-08-19 -> '19/08/2026'
    """
    return d.strftime("%d/%m/%Y")


def normalize_api_date(raw_date: Any) -> Optional[datetime.date]:
    """
    Parses various date formats returned by data.gov.in (DD/MM/YYYY, D/M/YYYY, YYYY-MM-DD, DD-MM-YYYY)
    into an internal datetime.date object.
    """
    if isinstance(raw_date, datetime.date):
        return raw_date
    if isinstance(raw_date, datetime.datetime):
        return raw_date.date()
    if isinstance(raw_date, str):
        clean_str = raw_date.strip()
        for fmt in (
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d %b %Y",
            "%d %B %Y",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ"
        ):
            try:
                return datetime.datetime.strptime(clean_str, fmt).date()
            except ValueError:
                continue
    return None


def add_days(d: datetime.date, days: int) -> datetime.date:
    """Adds or subtracts days from a datetime.date object."""
    return d + datetime.timedelta(days=days)


def get_date_sequence(start_date: datetime.date, num_days: int) -> List[datetime.date]:
    """Return a sequence of dates starting from start_date for num_days."""
    return [start_date + datetime.timedelta(days=i) for i in range(num_days)]


def get_rolling_date_range(lookback_days: int = 14, end_date: Optional[datetime.date] = None) -> Tuple[datetime.date, datetime.date]:
    """Return start_date and end_date for a rolling lookback window."""
    if end_date is None:
        end_date = get_ist_today()
    start_date = end_date - datetime.timedelta(days=lookback_days)
    return start_date, end_date
