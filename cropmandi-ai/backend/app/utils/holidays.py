from datetime import date
from typing import Tuple, Dict

# Major Indian Public & Festival Holidays mapped by (month, day) or specific date strings YYYY-MM-DD
# Covers fixed national holidays and major APMC market holiday calendar dates
FIXED_HOLIDAYS: Dict[Tuple[int, int], str] = {
    (1, 26): "Republic Day",
    (5, 1): "May Day / Labour Day",
    (8, 15): "Independence Day",
    (10, 2): "Gandhi Jayanti",
    (12, 25): "Christmas Day",
}

# Floating/Festival Holidays for 2026 (and general years)
SPECIFIC_HOLIDAYS_2026: Dict[date, str] = {
    date(2026, 1, 14): "Makar Sankranti / Pongal",
    date(2026, 1, 15): "Kanuma / Pongal",
    date(2026, 2, 15): "Maha Shivratri",
    date(2026, 3, 3): "Holi",
    date(2026, 3, 19): "Ugadi (Telugu New Year)",
    date(2026, 3, 20): "Ramzan / Eid-ul-Fitr",
    date(2026, 3, 27): "Sri Rama Navami",
    date(2026, 4, 3): "Good Friday",
    date(2026, 4, 14): "Dr. B.R. Ambedkar Jayanti",
    date(2026, 5, 27): "Bakrid / Eid-ul-Adha",
    date(2026, 6, 26): "Muharram",
    date(2026, 8, 15): "Independence Day",
    date(2026, 8, 26): "Milad-un-Nabi",
    date(2026, 9, 14): "Vinayaka Chaturthi / Ganesh Chaturthi",
    date(2026, 10, 2): "Mahatma Gandhi Jayanti",
    date(2026, 10, 19): "Maha Navami / Ayudha Puja",
    date(2026, 10, 20): "Vijayadasami / Dussehra",
    date(2026, 11, 8): "Deepavali / Diwali",
    date(2026, 11, 24): "Guru Nanak Jayanti",
    date(2026, 12, 25): "Christmas",
}


def check_market_holiday(d: date) -> Tuple[bool, str]:
    """
    Determines whether a mandi market is closed on date 'd'.
    Returns (True, reason) if it's a Sunday or a recognized festival/public holiday.
    Returns (False, "") if it's a regular trading day.
    """
    # 1. Sunday check (weekday == 6 in Python: 0=Mon, ..., 6=Sun)
    if d.weekday() == 6:
        return True, "Sunday (Weekly Mandi Holiday)"

    # 2. Specific year festival holiday check
    if d in SPECIFIC_HOLIDAYS_2026:
        return True, f"{SPECIFIC_HOLIDAYS_2026[d]} (Public/Festival Holiday)"

    # 3. Fixed annual holiday check (Month, Day)
    key = (d.month, d.day)
    if key in FIXED_HOLIDAYS:
        return True, f"{FIXED_HOLIDAYS[key]} (National Public Holiday)"

    return False, ""
