# Campañas de Marketing

## Python

[Implementacion](../../src/retailventure_dss/etl/models/campanas_marketing.py)

## CSV

```mermaid
erDiagram
    campanas_marketing {
        string campana_id
        string cliente_id
        string tipo_campana
        date   fecha_envio
        string canal_campana
        bool   abierto
        bool   convertido
        float  descuento_ofrecido
    }
```

| atributo           | formato      |
| ------------------ | ------------ |
| campana_id         | `CAM0000000` |
| cliente_id         | `CLI00000`   |
| fecha_envio        | `yyyy-mm-dd` |
| abierto            | `0\|1`       |
| convertido         | `0\|1`       |
| descuento_ofrecido | `0.00`       |

### Restricciones

- descuento_ofrecido >= 0.00
