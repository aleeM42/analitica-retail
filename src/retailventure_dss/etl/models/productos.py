from retailventure_dss.common.types.id_format import IdProducto
from pydantic import BaseModel, Field


class Productos(BaseModel):
    producto_id: IdProducto
    nombre: str = Field(min_length=1)
    categoria: str = Field(min_length=1)
    subcategoria: str = Field(min_length=1)
    costo: float = Field(ge=0.00)
    precio_lista: float = Field(ge=0.00)
    margen_bruto_pct: float = Field(ge=0.0)

    def get_id(self):
        return self.producto_id
