from datetime import datetime
from extract_datetime import extract_datetime

ACTION_VERBS = [
    "submit", "send", "review", "check", "complete",
    "share", "provide", "confirm", "update",
    "approve", "deliver", "finish", "feedback",
]


def extract_tasks(sentences: list[str], base_time: datetime) -> list[dict]:
    """
    Given a list of sentences and a base_time (datetime),
    return a list of task dicts with inferred date/time when present.

    Each task dict:
    {
        "task": <original sentence>,
        "date": <YYYY-MM-DD or None>,
        "time": <HH:MM or None>,
    }
    """
    tasks: list[dict] = []

    for s in sentences:
        s_lower = s.lower()

        # Only treat sentences containing at least one action verb as tasks
        if any(v in s_lower for v in ACTION_VERBS):
            dt = extract_datetime(s, base_time)

            if dt is not None:
                tasks.append({
                    "task": s,
                    "date": dt.date().isoformat(),
                    "time": dt.time().strftime("%H:%M"),
                })
            else:
                tasks.append({
                    "task": s,
                    "date": None,
                    "time": None,
                })

    return tasks
