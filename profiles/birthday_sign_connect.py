from datetime import datetime
from data import SIGNS_DATA

def sun_sign_from_birthday(birthday: datetime) -> str:
    """
    Look up which sign from the signs.json dataset based on the given date

    Args: 
        birthday: ISO date string, "YYYY-MM-DD"
    Returns:
        Sign name, eg. "Aries"
    Raises:
        ValueError: If the date is invalid or does not match any sign
    """

    date = datetime.strptime(birthday, "%Y-%m-%d")
    month, day = date.month, date.day 

    for sign_name, sign_data in SIGNS_DATA.items():
        start_mm, start_dd = _parse_md(sign_data["date_range"][0])
        end_mm, end_dd = _parse_md(sign_data["date_range"][1])
        
        if _date_in_range(month, day, start_mm, start_dd, end_mm, end_dd):
            return sign_name
    
    raise ValueError(f"No sign found for date {birthday} — check signs.json")


def _parse_md(md_string: str) -> tuple[int, int]:
    """Parse a 'MM-DD' string into (month, day)."""
    mm, dd = md_string.split("-")
    return int(mm), int(dd)

def _date_in_range(
    month: int, day: int,
    start_mm: int, start_dd: int,
    end_mm: int, end_dd: int,
) -> bool:
    """
    Check if (month, day) falls within [start, end] inclusive.
    
    Handles the year-wrap case for Capricorn (Dec 22 - Jan 19).
    """
    if start_mm <= end_mm:
        # Normal case: range doesn't cross year boundary
        if month < start_mm or month > end_mm:
            return False
        if month == start_mm and day < start_dd:
            return False
        if month == end_mm and day > end_dd:
            return False
        return True
    else:
        # Year-wrap case (e.g. Dec 22 - Jan 19)
        if month > start_mm or month < end_mm:
            return True
        if month == start_mm and day >= start_dd:
            return True
        if month == end_mm and day <= end_dd:
            return True
        return False