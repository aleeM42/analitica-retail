from retailventure_dss.common.types.id_format import IdInteraccion, IdCliente
from retailventure_dss.common.types.custom_date_format import CustomDateFormat
from pydantic import BaseModel, Field, field_validator
from datetime import date

from retailventure_dss.etl.models.util import validate_no_future_date


class Interaccion(BaseModel):
    interaccion_id: IdInteraccion
    cliente_id: IdCliente
    tipo: str = Field(min_length=1)
    fecha: CustomDateFormat
    canal: str = Field(min_length=1)
    resolucion: str = Field(min_length=1)
    tiempo_respuesta_hrs: float

    @field_validator("fecha")
    @classmethod
    def validate_no_future_date(cls, value: date) -> date:
        return validate_no_future_date(value, "La fecha no puede ser futura")

    def get_id(self):
        return self.interaccion_id
