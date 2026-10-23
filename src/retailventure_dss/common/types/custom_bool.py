from typing import Annotated
from pydantic import BeforeValidator
from typeguard import typechecked


@typechecked
def _int_to_bool(value: int | str) -> bool:

    if str(value) in ("1", "True", "true"):
        return True
    if str(value) in ("0", "False", "false"):
        return False
    raise ValueError("Invalid value")


CustomBool = Annotated[bool, BeforeValidator(_int_to_bool)]
