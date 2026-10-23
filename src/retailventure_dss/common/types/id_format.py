from typing import runtime_checkable

from retailventure_dss.common.types.pydantic_compatible import PydanticCompatible
from re import fullmatch, Pattern

from abc import ABC, abstractmethod


def _has_pattern(pattern: str | Pattern[str], target: str) -> bool:
    return fullmatch(pattern, target) is not None


class IdFormat(ABC, PydanticCompatible):
    id: str

    @staticmethod
    @abstractmethod
    def validate_format(value: str) -> str:
        pass

    def __init__(self, id: str) -> None:
        if self.validate_format(id) == "":
            raise ValueError(
                f"Given Id doesnt match expected format for {self.__class__.__name__}"
            )
        self.id = id

    def __str__(self) -> str:
        return f"{self.id}"

    def __repr__(self) -> str:
        return f"{self.id}"


class IdProducto(IdFormat):
    @staticmethod
    def validate_format(value: str) -> str:
        attempt = value.upper()
        return attempt if _has_pattern(r"PRD\d{4}", attempt) else ""


class IdCliente(IdFormat):
    @staticmethod
    def validate_format(value: str) -> str:
        attempt = value.upper()
        return attempt if _has_pattern(r"CLI\d{5}", attempt) else ""


class IdCampania(IdFormat):
    @staticmethod
    def validate_format(value: str) -> str:
        attempt = value.upper()
        return attempt if _has_pattern(r"CAM\d{7}", attempt) else ""


class IdDevolucion(IdFormat):
    @staticmethod
    def validate_format(value: str) -> str:
        attempt = value.upper()
        return attempt if _has_pattern(r"DEV\d{6}", attempt) else ""


class IdTransaccion(IdFormat):
    @staticmethod
    def validate_format(value: str) -> str:
        attempt = value.upper()
        return attempt if _has_pattern(r"TRX\d{7}", attempt) else ""


class IdInteraccion(IdFormat):
    @staticmethod
    def validate_format(value: str) -> str:
        attempt = value.upper()
        return attempt if _has_pattern(r"INT\d{7}", attempt) else ""
