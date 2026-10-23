# Analitica Retail

**Sistema de Soporte de Decisiones** (DSS) para empresa de retail.

## Tecnologias

- cargar csv: pandas
- bd/data warehouse: duckdb
- calculo estadistico y analista: PyMC-Marketing puede hacer cosas como: valor de cliente, churn y efectividad de descuentos, analisis jerarquico de anomalias en devoluciones e inferencia causal de atencion al cliente
- visualizacion: plotly dash

## Estructura de Directorios

```txt
./
├── data/
│   ├── in/                 # Archivos que lee el sistema (los csv)
│   └── out/                # Archivos que escribe el sistema (logs, db, etc)
├── docs/
│   └── data_format         # Informacion sobre estructura de datos de los csv
├── src/                    # Codigo
│   └── retailventure_dss/
│       ├── common/         # Reutilizables
│       ├── etl/            # Codigo para guardar los datos validados en el data warehouse
│       │  └── models/      # Clases de validacion de datos CSV
│       ├── data_access/    # Capa de accesos/consumo de datos (bd)
│       ├── analytics/      # Capa logica (Procesamiento)
│       └── interface/      # Capa de presentacion
└── tests/                  # Pruebas (si da chance)
```

---

## Requerimientos

### Funcionales

#### Preparación y Auditoría de Calidad de Datos

- [x] El sistema debe identificar los valores inconsistentes dentro de los datasets:
  - [x] Valores nulos
  - [x] Duplicados
  - [x] Outliers
  - [x] Registros inconsistentes.
- [x] El sistema debe extraer los datos de los datasets siguiendo estrictamente la estructura y tipos de datos definidos.
- [x] El sistema debe evaluar las metricas de calidad del dato (completitud, consistencia, unicidad y oportunidad por cada dataset).
  - [x] Calcular las metricas de calidad del dato
  - [x] Reportar las metricas de calidad del dato
- [x] El sistema debe generar un registro de los valores inconsistentes detectados

#### Análisis de Rentabilidad y Comportamiento de Compra

- [ ] El sistema debe identificar las siguientes categorias en los datos de los datasets:
  - [ ] Los segmentos de clientes
  - [ ] Categorías de producto
  - [ ] Canales de venta con mayor contribución al margen bruto total
  - [ ] Canales de venta con menor contribución al margen bruto total

- [x] El sistema debe calcular el _Customer Lifetime Value_ (CLV) estimado por segmento
- [ ] El sistema debe detectar cuáles segmentos están en declive

- [ ] El sistema debe analizar la estacionalidad de las ventas, mediante:
  - [ ] Identificar picos
  - [ ] Valles
  - [ ] Tendencias por categoría de producto
  - [ ] Tendencias por categoría de canal

- [x] El sistema debe identificar si los descuentos generan volumen suficiente para compersar la perdida de margen

#### Detección de Fugas de Ingresos

- [ ] El sistema debe analizar el patron de devoluciones mediante las siguientes acciones:
  - [ ] Detectar si los siguientes items tienen tasas anomalas:
    - [ ] productos
    - [ ] categorías
    - [ ] segmentos
  - [ ] Detectar clientes recurrentes en devoluciones
- [ ] El sistema debe detectar el impacto de las quejas no resueltas en la frecuencia de compra
- [x] El sistema debe identificar clientes en riesgo de _churn_
  - [ ] Definir metrica de inactividad
  - [ ] Encontrar el segmento de mayor valor en riesgo
- [ ] El sistema debe cuantificar el impacto economico estimado de las fugas identificadas
- [ ] El sistema debe expresar el impacto de las fugas en terminos de ingresos perdidos proyectados a 6 meses

#### Evaluación de la Efectividad del Marketing

- [ ] El sistema debe identificar las combinaciones de campañas de marketing que generan el mayor retorno mediante el calculo de:
  - [ ] tasa de conversion por tipo de campaña
  - [ ] canal de envio
  - [ ] segmento de cliente
- [ ] El sistema debe determinar si existe un efecto del descuento ofrecido en la campaña sobre la conversión, controlando por segmento.
- [ ] El sistema debe identificar el segmento de clientes que recibe campañas pero no convierte
- [ ] El sistema debe proponer hipótesis sobre las causas de clientes que reciben campañas pero no convierten basadas en los datos de CRM y devoluciones.

- [ ] El sistema debe calcular el ROI estimado de cada tipo de campaña usando el monto de compra convertida versus el costo implícito del descuento ofrecido.

#### Storytelling Ejecutivo y Recomendaciones

- [ ] El sistema debe mostrar un relato de datos cohesionado que conecte los hallazgos de las actividades anteriores en una narrativa con:
  - [ ] Inicio (situación actual)
  - [ ] Nudo (hallazgos clave y patrones detectados)
  - [ ] Desenlace (recomendaciones priorizadas).
- [ ] El sistema debe mostrar un dashboard ejecutiva con **máximo 10 visualizaciones**
- [ ] El sistema debe cuantificar el impacto potencial de al menos tres recomendaciones
- [ ] Cada visualización debe tener un título en forma de insight, no de descripción (ej: _"El canal digital genera el 40% del ingreso pero solo el 12% del margen neto"_).
- [ ] Las recomoendacionas se deben expresar cada una como _"Si hacemos X, esperamos un incremento/reducción de Y% en Z métrica, equivalente a \[monto] en ingresos"_.

## [Enunciado](./proyecto.md)
