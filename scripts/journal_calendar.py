"""Dated Journal/Dream calendar; historical dates retain their original bounds."""
from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo

LEGACY_TIMEZONE = "America/Denver"
CURRENT_TIMEZONE = "America/New_York"
TRANSITION_DAY = date(2026, 9, 5)
POLICY_ID = "journal-calendar-eastern-20260905-v1"


def timezone_name(day: date) -> str:
    return LEGACY_TIMEZONE if day < TRANSITION_DAY else CURRENT_TIMEZONE


def day_bounds(day: date) -> tuple[datetime, datetime]:
    # The transition starts at the preceding Denver day's end, then closes
    # at Eastern midnight. Half-open intervals prevent gaps and double counting.
    start_zone = LEGACY_TIMEZONE if day <= TRANSITION_DAY else CURRENT_TIMEZONE
    start = datetime.combine(day, time.min, tzinfo=ZoneInfo(start_zone))
    end = datetime.combine(day + timedelta(days=1), time.min,
                           tzinfo=ZoneInfo(timezone_name(day)))
    return start.astimezone(timezone.utc), end.astimezone(timezone.utc)


def current_date(when: datetime | None = None) -> date:
    when = when or datetime.now(timezone.utc)
    if when.tzinfo is None:
        raise ValueError("Calendar timestamp must include a timezone")
    transition_start, _ = day_bounds(TRANSITION_DAY)
    zone = LEGACY_TIMEZONE if when < transition_start else CURRENT_TIMEZONE
    return when.astimezone(ZoneInfo(zone)).date()


def metadata(day: date) -> dict:
    start, end = day_bounds(day)
    return {"policy_id": POLICY_ID, "timezone": timezone_name(day),
            "transition_day": day == TRANSITION_DAY,
            "start": start.isoformat(), "end": end.isoformat()}
