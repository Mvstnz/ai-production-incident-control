"""Demo business calendar. The persisted scope clock never changes n8n's clock."""
import json
from datetime import timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

SLA=json.loads((Path(__file__).resolve().parents[1]/"config"/"sla-policy.v1.json").read_text())


def add_business_hours(instant,hours):
    calendar=SLA["business_calendar"]
    local=instant.astimezone(ZoneInfo(calendar["timezone"])); remaining=hours*3600
    while remaining>0:
        if local.weekday() not in calendar["weekdays"] or local.hour>=calendar["close_hour"]:
            local=(local+timedelta(days=1)).replace(hour=calendar["open_hour"],minute=0,second=0,microsecond=0)
            continue
        if local.hour<calendar["open_hour"]: local=local.replace(hour=calendar["open_hour"],minute=0,second=0,microsecond=0)
        closing=local.replace(hour=calendar["close_hour"],minute=0,second=0,microsecond=0)
        consume=min(remaining,(closing-local).total_seconds())
        remaining-=consume;local+=timedelta(seconds=consume)
    return local
