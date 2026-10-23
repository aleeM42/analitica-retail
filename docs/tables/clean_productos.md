# clean_productos

## representacion

```mermaid
erDiagram
    clean_productos {
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
|  |  |  |  | CHECK (costo >= 0.00) | CHECK (precio_lista >= 0.00) | CHECK (margen_bruto_pct >= 0.0) |
