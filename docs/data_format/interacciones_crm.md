# Interacciones CRM

## Python

[Implementacion](../../src/retailventure_dss/etl/models/interacciones_crm.py)

## CSV

```mermaid
erDiagram
    interacciones_crm {
        string interaccion_id
        string cliente_id
        string tipo
        date   fecha
        string canal
        string resolucion
        float  tiempo_respuesta_hrs
    }
```

| atributo             | formato      |
| -------------------- | ------------ |
| interaccion_id       | `INT0000000` |
| cliente_id           | `CLI00000`   |
| fecha                | `yyyy-mm-dd` |
| tiempo_respuesta_hrs | `0.0`        |

### Restricciones

- tiempo_respuesta_hrs >= 0.0
