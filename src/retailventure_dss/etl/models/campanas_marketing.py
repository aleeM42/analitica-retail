from retailventure_dss.common.types.custom_bool import CustomBool
from retailventure_dss.common.types.id_format import IdCampania, IdCliente
from retailventure_dss.common.types.custom_date_format import CustomDateFormat
from pydantic import BaseModel, Field


class Campana(BaseModel):
    campana_id: IdCampania
    cliente_id: IdCliente
    tipo_campana: str = Field(min_length=1)
    fecha_envio: CustomDateFormat
    canal_campana: str = Field(min_length=1)
    abierto: CustomBool
    convertido: CustomBool
    descuento_ofrecido: float = Field(ge=0.00, le=1.00)

    def get_id(self):
        return self.campana_id
