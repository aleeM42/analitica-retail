# clean_devoluciones

## representacion

```mermaid
erDiagram
    clean_devoluciones {
        VARCHAR devolucion_id PK
        VARCHAR transaccion_id FK
        VARCHAR cliente_id FK
        VARCHAR motivo
        DECIMAL(10,2) monto_devuelto
        DATE fecha_devolucion
    }
```

| devolucion_id | transaccion_id | cliente_id | motivo | monto_devuelto | fecha_devolucion |
| --- | --- | --- | --- | --- | --- |
| pk |  |  |  |  |  |
|  | fk | fk |  |  |  |
| VARCHAR | VARCHAR | VARCHAR | VARCHAR | DECIMAL(10, 2) | DATE |
|  | NOT NULL, FOREIGN KEY -> clean_transacciones(transaccion_id) | NOT NULL, FOREIGN KEY -> clean_clientes(cliente_id) |  | CHECK (monto_devuelto >= 0.00) |  |
