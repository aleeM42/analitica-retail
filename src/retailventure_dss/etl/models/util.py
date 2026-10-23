from datetime import date


def validate_no_future_date(value: date, err_msg: str) -> date:
    if value > date.today():
        raise ValueError(err_msg)
    return value
