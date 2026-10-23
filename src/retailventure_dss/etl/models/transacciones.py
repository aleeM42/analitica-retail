from datetime import date

from retailventure_dss.common.types.custom_date_format import CustomDateFormat
from retailventure_dss.common.types.id_format import (
    IdTransaccion,
    IdCliente,
    IdProducto,
)
from pydantic import BaseModel, Field, field_validator

from retailventure_dss.etl.models.util import validate_no_future_date


class Transacciones(BaseModel):
    transaccion_id: IdTransaccion
    cliente_id: IdCliente
    fecha: CustomDateFormat
    producto_id: IdProducto
    cantidad: int = Field(gt=0)
    precio_unitario: float = Field(gt=0.00)
    descuento: float = Field(ge=0.000, le=1.000)
    monto_neto: float = Field(gt=0.00)
    canal: str = Field(min_length=1)
    metodo_pago: str = Field(min_length=1)

    @field_validator("fecha")
    @classmethod
    def validate_no_future_date(cls, value: date) -> date:
        return validate_no_future_date(value, "La fecha no puede ser futura")

    def get_id(self):
        return self.transaccion_id
