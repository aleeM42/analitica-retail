from retailventure_dss.common.types.pydantic_compatible import PydanticCompatible


class Gender(PydanticCompatible):
    gender: str

    def __init__(self, gender: str) -> None:
        attempt = gender.upper()

        if attempt == "F":
            normalized = "F"
        elif attempt == "M":
            normalized = "M"
        elif attempt == "NO ESPECIFICADO":
            normalized = "ND"
        else:
            raise ValueError("Invalid gender option")
        self.gender = normalized

    def __str__(self) -> str:
        return f"{self.gender}"

    def __repr__(self) -> str:
        return f"{self.gender}"
