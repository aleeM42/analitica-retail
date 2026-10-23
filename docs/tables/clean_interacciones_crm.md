# clean_interacciones_crm

## representacion

```mermaid
erDiagram
    clean_interacciones_crm {
        VARCHAR interaccion_id PK
        VARCHAR cliente_id FK
        VARCHAR tipo
        DATE fecha
        VARCHAR canal
        VARCHAR resolucion
        DECIMAL(10,2) tiempo_respuesta_hrs
    }
```

| interaccion_id | cliente_id | tipo | fecha | canal | resolucion | tiempo_respuesta_hrs |
| --- | --- | --- | --- | --- | --- | --- |
| pk |  |  |  |  |  |  |
|  | fk |  |  |  |  |  |
| VARCHAR | VARCHAR | VARCHAR | DATE | VARCHAR | VARCHAR | DECIMAL(10, 2) |
|  | NOT NULL, FOREIGN KEY -> clean_clientes(cliente_id) |  |  |  |  | CHECK (tiempo_respuesta_hrs >= 0.0) |
