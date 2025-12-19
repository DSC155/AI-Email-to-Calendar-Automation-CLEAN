from datetime import datetime, time, timedelta
from dateparser.search import search_dates
import re

TIME_HINTS = {
    "early morning": time(8, 0),
    "morning": time(9, 0),
    "late morning": time(11, 0),
    "noon": time(12, 0),
    "midday": time(12, 0),
    "early afternoon": time(13, 0),
    "afternoon": time(14, 0),
    "late afternoon": time(16, 0),
    "early evening": time(17, 0),
    "evening": time(18, 0),
    "late evening": time(20, 0),
    "night": time(21, 0),
    "midnight": time(0, 0),
    "eod": time(17, 0),
    "eob": time(17, 0),
    "end of business": time(17, 0),
    "asap": time(9, 0),
    "immediately": time(9, 0),
    "at the earliest": time(9, 0),
}


def make_naive(dt: datetime) -> datetime:
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def extract_datetime(text: str, base_time: datetime) -> datetime | None:
    now = base_time
    lower = text.lower()

    # --- hard rule: "within N days" -> base_time + N days at 09:00
    m = re.search(r"within\s+(\d+)\s+day", lower)
    if m:
        n = int(m.group(1))
        target = now + timedelta(days=n)
        return target.replace(hour=9, minute=0)

    # normalize for dateparser: "within" -> "in"
    normalized = lower.replace("within ", "in ")

    results = search_dates(
        normalized,
        settings={
            "PREFER_DATES_FROM": "future",
            "RELATIVE_BASE": now,
            "RETURN_AS_TIMEZONE_AWARE": True,
        },
    )

    if not results:
        return None

    future_dates: list[datetime] = []
    for _, dt in results:
        dt = make_naive(dt)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=base_time.tzinfo)
        if dt > now:
            future_dates.append(dt)

    if not future_dates:
        return None

    dt = min(future_dates)

    # explicit clock time wins
    time_match = re.search(r"(\d{1,2})(?:[:.](\d{2}))?\s*(am|pm)", text, re.I)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2) or 0)
        meridian = time_match.group(3).lower()

        if meridian == "pm" and hour != 12:
            hour += 12
        if meridian == "am" and hour == 12:
            hour = 0

        return dt.replace(hour=hour, minute=minute)

    # infer from hints (handles "end of day today")
    inferred = None
    for phrase in sorted(TIME_HINTS, key=len, reverse=True):
        if re.search(rf"\b{re.escape(phrase)}\b", lower):
            inferred = TIME_HINTS[phrase]
            break

    if inferred:
        dt = dt.replace(hour=inferred.hour, minute=inferred.minute)
    elif dt.hour == 0 and dt.minute == 0:
        dt = dt.replace(hour=9, minute=0)

    return dt
