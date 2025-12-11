"""
Semester utility functions for automatic detection of current/upcoming semesters.

CMU Academic Calendar:
- Fall: September - December
- Spring: January - May
- Summer: June - August

Semester Code Format: {f|s|m}{YY}
- f = Fall, s = Spring, m = Summer (miniterm)
- YY = 2-digit year (e.g., 25 = 2025)
"""

from datetime import datetime


def get_current_semester() -> str:
    """
    Get current semester code based on today's date.

    Returns: Semester code like 'f25', 's26', 'm26'
    """
    today = datetime.now()
    year = today.year % 100  # Get 2-digit year (2025 -> 25)
    month = today.month

    if month >= 9:  # September - December -> Fall
        return f"f{year}"
    elif month >= 6:  # June - August -> Summer
        return f"m{year}"
    else:  # January - May -> Spring
        return f"s{year}"


def get_upcoming_semester() -> str:
    """
    Get the upcoming/next semester to fetch courses for.

    This is the semester that course registration would typically target:
    - December: Registration for Spring (next year)
    - Jan-May: Currently in Spring semester
    - Jun-Aug: Registration for Fall
    - Sep-Nov: Currently in Fall semester

    Returns: Semester code like 'f25', 's26'
    """
    today = datetime.now()
    year = today.year % 100
    month = today.month

    if month >= 12:  # December -> Spring next year
        return f"s{year + 1}"
    elif month >= 9:  # Sep-Nov -> Currently Fall
        return f"f{year}"
    elif month >= 6:  # Jun-Aug -> Fall same year
        return f"f{year}"
    else:  # Jan-May -> Currently Spring
        return f"s{year}"


def get_semester_options() -> list:
    """
    Generate dynamic semester options for dropdown.

    Returns: List of (value, label, is_default) tuples.
    """
    today = datetime.now()
    year = today.year % 100

    current = get_upcoming_semester()

    options = [
        (f"s{year}", f"Spring {2000+year} (s{year})", f"s{year}" == current),
        (f"m{year}", f"Summer {2000+year} (m{year})", f"m{year}" == current),
        (f"f{year}", f"Fall {2000+year} (f{year})", f"f{year}" == current),
        (f"s{year+1}", f"Spring {2000+year+1} (s{year+1})", f"s{year+1}" == current),
        (f"f{year-1}", f"Fall {2000+year-1} (f{year-1})", False),  # Previous year option
    ]

    return options


def get_semester_label(code: str) -> str:
    """
    Convert semester code to human-readable label.

    Args:
        code: Semester code like 'f25', 's26'

    Returns: Label like 'Fall 2025', 'Spring 2026'
    """
    if len(code) < 3:
        return code

    prefix = code[0].lower()
    year = int(code[1:]) + 2000

    names = {'f': 'Fall', 's': 'Spring', 'm': 'Summer'}
    name = names.get(prefix, prefix.upper())

    return f"{name} {year}"
