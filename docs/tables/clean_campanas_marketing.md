# clean_campanas_marketing

## representacion

```mermaid
erDiagram
    clean_campanas_marketing {
        VARCHAR campana_id PK
        VARCHAR cliente_id FK
        VARCHAR tipo_campana
        DATE fecha_envio
        VARCHAR canal_campana
        BOOLEAN abierto
        BOOLEAN convertido
        DECIMAL(10,2) descuento_ofrecido
    }
```

| campana_id | cliente_id | tipo_campana | fecha_envio | canal_campana | abierto | convertido | descuento_ofrecido |
| --- | --- | --- | --- | --- | --- | --- | --- |
| pk |  |  |  |  |  |  |  |
|  | fk |  |  |  |  |  |  |
| VARCHAR | VARCHAR | VARCHAR | DATE | VARCHAR | BOOLEAN | BOOLEAN | DECIMAL(10, 2) |
|  | NOT NULL, FOREIGN KEY -> clean_clientes(cliente_id) |  |  |  |  |  | CHECK (descuento_ofrecido >= 0.00) |
