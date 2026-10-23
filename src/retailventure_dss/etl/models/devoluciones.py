from retailventure_dss.common.types.id_format import (
    IdDevolucion,
    IdTransaccion,
    IdCliente,
)
from pydantic import BaseModel, Field
from retailventure_dss.common.types.custom_date_format import CustomDateFormat


class Devolucion(BaseModel):
    devolucion_id: IdDevolucion
    transaccion_id: IdTransaccion
    cliente_id: IdCliente
    motivo: str = Field(min_length=1)
    monto_devuelto: float = Field(ge=0.00)
    fecha_devolucion: CustomDateFormat

    def get_id(self):
        return self.devolucion_id
