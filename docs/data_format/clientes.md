# Clientes

## Python

[Implementacion](../../src/retailventure_dss/etl/models/clientes.py)

## CSV

```mermaid
erDiagram
    cliente {
        string cliente_id
        uint   edad
        char   genero
        string ciudad
        string segmento
        date   fecha_registro
        string canal_adquisicion
    }
```

| atributo       | formato                 |
| -------------- | ----------------------- |
| cliente_id     | `CLI00000`              |
| genero         | `M\|F\|No especificado` |
| fecha_registro | `yyyy-mm-dd`            |
