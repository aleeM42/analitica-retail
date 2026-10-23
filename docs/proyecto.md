# INFORMÁTICA - Ingeniería

## Tópicos Especiales para la Gestión de Datos

**Prof. Armen Djenanian**

---

### Proyecto 01: Retail Intelligence - Storytelling con Datos para Maximizar la Rentabilidad y Prevenir Fugas de Ingresos

#### Objetivo

Desarrollar un análisis exploratorio completo sobre un conjunto de datos reales del sector retail, identificando patrones de comportamiento del consumidor, oportunidades de incremento de rentabilidad y señales tempranas de fuga de ingresos, para construir un storytelling de datos coherente, visualmente impactante y orientado a la toma de decisiones gerenciales.

#### Alcance

El equipo tiene libertad de elegir las herramientas de análisis y visualización (Python, R, Power BI, Tableau, Excel avanzado, etc.) y el enfoque narrativo del storytelling. Se valorará la profundidad del análisis sobre la cantidad de gráficos, la coherencia del relato de datos y la capacidad de traducir hallazgos técnicos en recomendaciones ejecutivas concretas y cuantificables.

---

### Contexto del Caso

**RetailVenture C.A.** es una cadena de retail con presencia en canales físicos y digitales que opera en Venezuela desde hace 12 años. La empresa enfrenta una presión creciente en sus márgenes:

- El ticket promedio ha caído un **8% interanual**,
- La tasa de devoluciones aumentó al **14%** en el último trimestre,
- La efectividad de las campañas de marketing ha disminuido de un **22% a un 11%** de conversión en 18 meses.

La gerencia general ha contratado al equipo para que, a partir de los datos operativos disponibles, construya un relato basado en evidencia que explique qué está ocurriendo, por qué está ocurriendo y qué acciones concretas se deben tomar.

---

### Set de Datos Provistos

El equipo recibirá seis archivos en formato CSV que simulan el entorno de datos de RetailVenture C.A. con 24 meses de historia operativa. Los datos son sintéticos pero semánticamente coherentes con la realidad del sector. El volumen aproximado es de **50,000 transacciones**, **8,000 clientes únicos** y **320 productos activos**.

| Archivo                  | Descripción                                                                              | Campos clave                                                                                                                               |
| :----------------------- | :--------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------- |
| `clientes.csv`           | Perfil demográfico y de segmentación de los clientes registrados en la plataforma.       | `cliente_id`, `edad`, `genero`, `ciudad`, `segmento`, `fecha_registro`, `canal_adquisicion`                                                |
| `transacciones.csv`      | Historial completo de compras: productos, montos, descuentos aplicados y canal de venta. | `transaccion_id`, `cliente_id`, `fecha`, `producto_id`, `cantidad`, `precio_unitario`, `descuento`, `canal` (online/tienda), `metodo_pago` |
| `productos.csv`          | Catálogo de productos con categoría, subcategoría, costo y margen bruto.                 | `producto_id`, `nombre`, `categoria`, `subcategoria`, `costo`, `precio_lista`, `margen_bruto_pct`                                          |
| `devoluciones.csv`       | Registro de devoluciones y motivos reportados por los clientes.                          | `devolucion_id`, `transaccion_id`, `cliente_id`, `motivo`, `monto_devuelto`, `fecha_devolucion`                                            |
| `interacciones_crm.csv`  | Eventos de contacto del cliente con la empresa: quejas, consultas y resolución.          | `interaccion_id`, `cliente_id`, `tipo` (queja/consulta/soporte), `fecha`, `canal`, `resolucion`, `tiempo_respuesta_hrs`                    |
| `campanas_marketing.csv` | Campañas enviadas a clientes y si resultaron en una compra (conversión).                 | `campana_id`, `cliente_id`, `tipo_campana`, `fecha_envio`, `canal_campana`, `abierto`, `convertido`, `descuento_ofrecido`                  |

---

### Actividades

#### A1. Preparación y Auditoría de Calidad de Datos

- Cargar los seis datasets e identificar valores nulos, duplicados, outliers y registros inconsistentes (ej: devoluciones sin transacción de origen, campañas con fechas posteriores a la compra).
- Documentar las decisiones de limpieza y transformación tomadas, justificando cada una técnicamente.
- Construir un modelo relacional conceptual que muestre cómo se relacionan los seis datasets entre sí (diagrama dimensional o esquema estrella).
- Calcular y reportar las métricas de calidad del dato: completitud, consistencia, unicidad y oportunidad por cada dataset.

#### A2. Análisis de Rentabilidad y Comportamiento de Compra

- Identificar los segmentos de clientes, categorías de producto y canales de venta con mayor y menor contribución al margen bruto total.
- Calcular el _Customer Lifetime Value_ (CLV) estimado por segmento y detectar cuáles segmentos están en declive.
- Analizar la estacionalidad de las ventas: identificar picos, valles y tendencias por categoría de producto y canal.
- Evaluar el efecto real de los descuentos sobre el margen: ¿los descuentos generan volumen suficiente para compensar la pérdida de margen?

#### A3. Detección de Fugas de Ingresos

- Analizar el patrón de devoluciones: ¿existen productos, categorías o segmentos con tasas anomalas? ¿Hay clientes recurrentes en devoluciones?
- Cruzar los datos de interacciones del CRM con el comportamiento de compra posterior: ¿los clientes que tuvieron quejas no resueltas disminuyeron su frecuencia de compra?
- Identificar clientes en riesgo de _churn_ (fuga): definir una métrica de inactividad y encontrar el segmento de mayor valor en riesgo.
- Cuantificar el impacto económico estimado de las fugas identificadas: expresarlo en términos de ingresos perdidos proyectados a 6 meses.

#### A4. Evaluación de la Efectividad del Marketing

- Calcular la tasa de conversión por tipo de campaña, canal de envío y segmento de cliente para identificar qué combinaciones generan el mayor retorno.
- Determinar si existe un efecto del descuento ofrecido en la campaña sobre la conversión, controlando por segmento.
- Identificar el segmento de clientes que recibe campañas pero no convierte, y proponer hipótesis sobre las causas basadas en los datos de CRM y devoluciones.
- Calcular el ROI estimado de cada tipo de campaña usando el monto de compra convertida versus el costo implícito del descuento ofrecido.

#### A5. Storytelling Ejecutivo y Recomendaciones

- Construir un relato de datos cohesionado que conecte los hallazgos de las actividades anteriores en una narrativa con inicio (situación actual), nudo (hallazgos clave y patrones detectados) y desenlace (recomendaciones priorizadas).
- Diseñar un dashboard o presentación ejecutiva con **máximo 10 visualizaciones**, seleccionadas por su poder explicativo, no por su cantidad. Cada visualización debe tener un título en forma de insight, no de descripción (ej: _"El canal digital genera el 40% del ingreso pero solo el 12% del margen neto"_).
- Cuantificar el impacto potencial de al menos tres recomendaciones: expresar cada una como _"Si hacemos X, esperamos un incremento/reducción de Y% en Z métrica, equivalente a [monto] en ingresos"_.
- Preparar una presentación de 15 minutos ante la gerencia (simulada en el aula) donde el equipo defienda sus hallazgos y recomendaciones ante preguntas de escrutinio técnico y de negocio.

---

### Evaluación

| Criterio de Evaluación                   | Descripción y Alcance                                                                                                                                                                                                                             |    %     | Niveles de Logro (0 - 20)                                                                                                                                                                                                                                                                                                                                    |
| :--------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------: | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1. Calidad y Auditoría de Datos**      | Completitud del perfil de calidad por dataset (nulos, duplicados, outliers), justificación técnica de las decisiones de limpieza y construcción del modelo relacional conceptual (ER o esquema estrella).                                         | **20%**  | **Exc:** Perfil completo, decisiones documentadas, modelo relacional sin errores.<br>**Bien:** Cumple los elementos clave con algún detalle menor.<br>**Reg:** Auditoría parcial o modelo relacional incorrecto.<br>**Def:** Ausencia de auditoría o modelo que no refleja las relaciones reales.                                                            |
| **2. Profundidad Analítica**             | Rigor en el análisis de rentabilidad (CLV, margen por canal/segmento), detección de fugas (devoluciones, churn, impacto CRM) y evaluación de marketing (conversión, ROI). Se penaliza la presentación de correlaciones sin investigar causalidad. | **30%**  | **Exc:** Cubre las 5 áreas, cuantifica impactos, distingue correlación de causalidad.<br>**Bien:** Cubre al menos 3 áreas con análisis sólido.<br>**Reg:** Análisis superficial o limitado a una sola área.<br>**Def:** No evidencia análisis real; solo estadísticos básicos sin interpretación.                                                            |
| **3. Calidad del Storytelling**          | Coherencia de la narrativa (inicio-nudo-desenlace), poder explicativo de las visualizaciones (máx. 10), calidad de los títulos como insights accionables y claridad en la cuantificación de recomendaciones (_"Si X, entonces Y% en Z"_).         | **25%**  | **Exc:** Narrativa fluida, visualizaciones con títulos de insight, 3+ recomendaciones cuantificadas.<br>**Bien:** Narración clara con alguna visualización o recomendación genérica sin cuantificar.<br>**Reg:** Historia fragmentada, gráficos sin títulos de insight.<br>**Def:** Sin narrativa coherente; colección de gráficos sin hilo conductor.       |
| **4. Defensa Oral y Escrutinio**         | Capacidad de todos los integrantes de responder preguntas técnicas y de negocio sin depender de las diapositivas. Se evaluará con preguntas de profundización sobre decisiones metodológicas y validez de los hallazgos.                          | **15%**  | **Exc:** Todo el equipo responde con precisión; justifican metodología al ser cuestionados.<br>**Bien:** Mayoría del equipo responde; algún integrante depende de las diapositivas.<br>**Reg:** Respuestas incompletas o solo 1-2 integrantes dominan el material.<br>**Def:** El equipo no puede defender los hallazgos ni explicar las decisiones tomadas. |
| **5. Bitácora de IA y Criterio Técnico** | Si se usaron herramientas de IA generativa: registro de prompts con validación técnica de resultados, indicando qué fue aceptado, ajustado o rechazado y por qué. Se valora el juicio crítico sobre la IA, no la aceptación ciega.                | **10%**  | **Exc:** Bitácora completa con validación técnica de cada sugerencia de IA aceptada o rechazada.<br>**Bien:** Bitácora presente con validación parcial.<br>**Reg:** Lista de prompts sin evidencia de validación crítica.<br>**Def:** Sin bitácora o evidencia de _vibe coding_ sin comprensión del código generado.                                         |
| **TOTAL**                                | **Suma de todos los criterios ponderados.**<br>_Nota mínima aprobatoria: $10/20$._                                                                                                                                                                | **100%** | **Fecha de entrega y defensa:** Semana 15.                                                                                                                                                                                                                                                                                                                   |
