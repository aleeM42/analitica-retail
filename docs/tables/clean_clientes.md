# clean_clientes

## representacion

```mermaid
erDiagram
    clean_clientes {
        VARCHAR cliente_id PK
        INTEGER edad
        VARCHAR genero
        VARCHAR ciudad
        VARCHAR segmento
        DATE fecha_registro
        VARCHAR canal_adquisicion
    }
```

| cliente_id | edad | genero | ciudad | segmento | fecha_registro | canal_adquisicion |
| --- | --- | --- | --- | --- | --- | --- |
| pk |  |  |  |  |  |  |
|  |  |  |  |  |  |  |
| VARCHAR | INTEGER | VARCHAR | VARCHAR | VARCHAR | DATE | VARCHAR |
|  |  | CHECK (genero IN ('M', 'F')) |  |  |  |  |
