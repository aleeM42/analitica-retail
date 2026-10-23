# stg_productos

## representacion

```mermaid
erDiagram
    stg_productos {
        VARCHAR producto_id PK
        VARCHAR nombre
        VARCHAR categoria
        VARCHAR subcategoria
        DECIMAL(10,2) costo
        DECIMAL(10,2) precio_lista
        DECIMAL(5,2) margen_bruto_pct
    }
```

| producto_id | nombre | categoria | subcategoria | costo | precio_lista | margen_bruto_pct |
| --- | --- | --- | --- | --- | --- | --- |
| pk |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
| VARCHAR | VARCHAR | VARCHAR | VARCHAR | DECIMAL(10, 2) | DECIMAL(10, 2) | DECIMAL(5, 2) |
|  |  |  |  |  |  |  |
