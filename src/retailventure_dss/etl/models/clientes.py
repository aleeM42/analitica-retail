from datetime import date

from retailventure_dss.common.types.custom_date_format import CustomDateFormat
from retailventure_dss.common.types.genders import Gender
from retailventure_dss.common.types.id_format import IdCliente

from pydantic import BaseModel, Field, field_validator
from retailventure_dss.etl.models.util import validate_no_future_date


class Cliente(BaseModel):
    cliente_id: IdCliente
    edad: int = Field(ge=0)
    genero: Gender
    ciudad: str = Field(min_length=1)
    segmento: str = Field(min_length=1)
    fecha_registro: CustomDateFormat
    canal_adquisicion: str = Field(min_length=1)

    @field_validator("fecha_registro")
    @classmethod
    def validate_no_future_date(cls, value: date) -> date:
        return validate_no_future_date(
            value, "La fecha de registro no puede ser futura"
        )

    def get_id(self):
        return self.cliente_id
