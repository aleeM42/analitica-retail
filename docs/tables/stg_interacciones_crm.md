# stg_interacciones_crm

## representacion

```mermaid
erDiagram
    stg_interacciones_crm {
        VARCHAR interaccion_id PK
        VARCHAR cliente_id
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
|  |  |  |  |  |  |  |
| VARCHAR | VARCHAR | VARCHAR | DATE | VARCHAR | VARCHAR | DECIMAL(10, 2) |
|  | NOT NULL |  |  |  |  |  |
