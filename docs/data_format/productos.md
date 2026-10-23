# productos

## Python

[Implementacion](../../src/retailventure_dss/etl/models/productos.py)

## CSV

```mermaid
erDiagram
    productos {
        string producto_id
        string nombre
        string categoria
        string subcategoria
        float  costo
        float  precio_lista
        float  margen_bruto_pct
    }
```

| atributo         | formato   |
| ---------------- | --------- |
| producto_id      | `PRD0000` |
| costo            | `0.00`    |
| precio_lista     | `0.00`    |
| margen_bruto_pct | `0.0`     |

### Restricciones

- costo >= 0.00
- precio_lista >= 0.00
- margen_bruto_pct >= 0.0
