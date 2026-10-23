# stg_transacciones

## representacion

```mermaid
erDiagram
    stg_transacciones {
        VARCHAR transaccion_id PK
        VARCHAR cliente_id
        DATE fecha
        VARCHAR producto_id
        INTEGER cantidad
        DECIMAL(10,2) precio_unitario
        DECIMAL(5,3) descuento
        DECIMAL(10,2) monto_neto
        VARCHAR canal
        VARCHAR metodo_pago
    }
```

| transaccion_id | cliente_id | fecha | producto_id | cantidad | precio_unitario | descuento | monto_neto | canal | metodo_pago |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pk |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |
| VARCHAR | VARCHAR | DATE | VARCHAR | INTEGER | DECIMAL(10, 2) | DECIMAL(5, 3) | DECIMAL(10, 2) | VARCHAR | VARCHAR |
|  | NOT NULL |  | NOT NULL |  |  |  |  |  |  |
