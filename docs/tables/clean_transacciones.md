# clean_transacciones

## representacion

```mermaid
erDiagram
    clean_transacciones {
        VARCHAR transaccion_id PK
        VARCHAR cliente_id FK
        DATE fecha
        VARCHAR producto_id FK
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
|  | fk |  | fk |  |  |  |  |  |  |
| VARCHAR | VARCHAR | DATE | VARCHAR | INTEGER | DECIMAL(10, 2) | DECIMAL(5, 3) | DECIMAL(10, 2) | VARCHAR | VARCHAR |
|  | NOT NULL, FOREIGN KEY -> clean_clientes(cliente_id) |  | NOT NULL, FOREIGN KEY -> clean_productos(producto_id) | CHECK (cantidad > 0) | CHECK (precio_unitario >= 0.00) | CHECK (descuento >= 0.000) | CHECK (monto_neto >= 0.00) |  |  |
