# stg_devoluciones

## representacion

```mermaid
erDiagram
    stg_devoluciones {
        VARCHAR devolucion_id PK
        VARCHAR transaccion_id
        VARCHAR cliente_id
        VARCHAR motivo
        DECIMAL(10,2) monto_devuelto
        DATE fecha_devolucion
    }
```

| devolucion_id | transaccion_id | cliente_id | motivo | monto_devuelto | fecha_devolucion |
| --- | --- | --- | --- | --- | --- |
| pk |  |  |  |  |  |
|  |  |  |  |  |  |
| VARCHAR | VARCHAR | VARCHAR | VARCHAR | DECIMAL(10, 2) | DATE |
|  | NOT NULL | NOT NULL |  |  |  |
