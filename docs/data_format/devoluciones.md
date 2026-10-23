# Devoluciones

## Python

[Implementacion](../../src/retailventure_dss/etl/models/devoluciones.py)

## CSV

```mermaid
erDiagram
    devoluciones {
        string devolucion_id
        string transaccion_id
        string cliente_id
        string motivo
        float  monto_devuelto
        date   fecha_devolucion
    }
```

| atributo         | formato      |
| ---------------- | ------------ |
| devolucion_id    | `DEV000000`  |
| transaccion_id   | `TRX0000000` |
| cliente_id       | `CLI00000`   |
| monto_devuelto   | `0.00`       |
| fecha_devolucion | `yyyy-mm-dd` |

### Restricciones

- monto_devuelto >= 0.00
