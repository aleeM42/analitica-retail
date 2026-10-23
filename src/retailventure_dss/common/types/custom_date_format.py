from datetime import date, datetime
from typing import Annotated
from pydantic import BeforeValidator
from typeguard import typechecked


@typechecked
def _format_to_date(value: str | date) -> date:
    if isinstance(value, date):
        return value
    formats = ["%Y-%m-%d", "%d-%m-%Y"]
    dt = None
    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            break
        except ValueError:
            dt = None
            continue

    if dt is None:
        raise ValueError("Invalid date format")

    return date(dt.year, dt.month, dt.day)


CustomDateFormat = Annotated[date, BeforeValidator(_format_to_date)]
