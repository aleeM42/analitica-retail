# Retail Intelligence: Márgenes en Crisis — El Plan de Rescate
## RetailVenture C.A. | Presentación Ejecutiva de Resultados
### Tópicos Especiales para la Gestión de Datos | Semana 15

---

## ESTRUCTURA DE LA PRESENTACIÓN (15 minutos)

| Bloque | Tiempo | Contenido |
|---|---|---|
| **Inicio** | 0:00–3:00 | Diagnóstico: los tres síntomas percibidos vs la realidad auditada |
| **Nudo** | 3:00–8:00 | Los cuatro frentes de fuga de ingresos con evidencia estadística |
| **Desenlace** | 8:00–11:30 | Plan de intervención: tres recomendaciones cuantificadas |
| **Escrutinio** | 11:30–15:00 | Sesión de preguntas técnicas y de negocio |

---

## 1. INICIO: El Espejismo del Crecimiento y la Crisis Silenciosa

> **Apertura ejecutiva:**
> RetailVenture C.A. cumple 12 años liderando el retail omnicanal en Venezuela. En los últimos 24 meses facturó **$17,392,987** y sus sistemas procesan 50,000 transacciones con 318 productos en tres canales. Los números absolutos parecen sólidos. Pero la auditoría profunda de los datos operativos cuenta la historia real.

### Los Tres Síntomas: Percepción Gerencial vs. Realidad de los Datos

| Indicador | Síntoma Reportado (Brief) | Realidad Auditada en Datos | Diagnóstico de Gestión |
|---|---|---|---|
| **Ticket promedio** | Caída del 8% interanual | Caída real de **-1.93%** ($351 a $344) | El volumen y gasto medio se sostienen; no hay colapso del consumo |
| **Tasa de devoluciones** | Aumento al 14% en Q4 | **13.45%** global y en 2024-Q4 | Estable en general, pero **crítico en 2 categorías (hasta 21.8%)** |
| **Conversión de marketing** | Descenso de 22% a 11% | Promedio **9.04%** (cae de 11.7% a 5.1%) | Caída real de más del 50% por saturación de base y fatiga de canal |

### La Pregunta Gerencial Central

> *¿Es una contracción generalizada del consumo en Venezuela… o un problema de gestión interna que podemos resolver?*

**La respuesta de los datos: es un problema interno de gestión y asignación.** Identificamos cuatro fuentes de fuga cuantificadas que suman **$395,954 anuales en margen operativo recuperable** (+$197,977 semestrales, una mejora directa del **+9.2%** sobre el margen bruto semestral actual), además de **$39,895 anuales en facturación preservada** contra abandono de clientes clave. Ninguna requiere más ventas para solucionarse; requieren decisiones operativas y analíticas quirúrgicas.

---

## 2. NUDO: Los Cuatro Frentes de Fuga de Ingresos

### Fuga #1: La Hemorragia Localizada en Devoluciones — **$547,567 en 24 meses**

- La tasa global de devoluciones es 13.45%, pero el problema **no es general**.
- Dos categorías concentran todo el exceso anómalo estadísticamente confirmado:

| Categoría | Tasa de Devolución | Tasa de Referencia (resto) | Exceso en 24 meses | Exceso Anualizado |
|---|---|---|---|---|
| **Ropa y Calzado** | **21.78%** | 11.79% | $147,250 | $73,625 |
| **Electrónica** | **17.65%** | 12.60% | $400,318 | $200,159 |
| **Total Exceso** | — | — | **$547,567** | **$273,784** |

- **Dimensión canal:** El canal Online factura el 37.6% de los ingresos pero su margen tras devoluciones es de apenas **9.5%** (vs 13.7% en tienda física), revelando una erosión de más de 4.1 pp por logística inversa mal gestionada en canales digitales.

### Fuga #2: La Falsa Salvación de los Descuentos Comerciales — **$483,850 en 12 meses**

- El sistema aplicó $967,700 en promociones y descuentos en los 24 meses del dataset ($483,850/año, $241,925/semestre).
- **El hallazgo estadístico clave:** Modelo OLS con efectos fijos por `producto_id` (el mismo producto comparado consigo mismo con y sin descuento) entrega un **coeficiente de elasticidad de ~0** (todos los intervalos de confianza al 95% cruzan el cero, p > 0.15).
- **Conclusión:** Los descuentos en precio de lista no generan volumen incremental. Se subsidia a clientes habituales que habrían comprado de todas formas al precio de lista.
- El techo del daño recuperable: **$241,925/semestre** si se eliminan los descuentos inelásticos.

### Fuga #3: Erosión Silenciosa de Clientes de Alto Valor — **$39,895 en riesgo semestral**

- Los segmentos Frecuente y Premium concentran el **80.7% del margen bruto total** (49.5% y 31.2% respectivamente).
- El modelo de supervivencia Kaplan-Meier por intervalos entre compras identificó **696 clientes** en estado "En riesgo" (silencio de compra que supera el percentil 90 de su patrón histórico, S(t) < 0.10).
- Pérdida esperada proyectada a 6 meses: **$39,895 en ingresos** ($9,820 en margen bruto semestral directo).
- El backtest del modelo (datos hasta junio 2024, validado contra jul-dic 2024) confirmó que los clientes marcados "En riesgo" presentaron una tasa de no retorno real del **26.6%** (frente a solo 1.9% en Premium activos y 10.2% en Frecuentes activos), confirmando la validez del semáforo para alertar fuga progresiva.

### Fuga #4: Desconexión y Desperdicio en Marketing — ROI Real vs ROI Aparente

- La tasa de conversión global colapsó a más de la mitad en los 24 meses: arrancó en **11.7% (2023-Q1)** y cerró en **5.1% (2024-Q4)**.
- **Análisis causal (Regresión Logística multivariada con controles):**
  - El descuento ofrecido en campaña sí incrementa la probabilidad de compra ($\beta = +3.285$, $p = 1.87 \times 10^{-14}$, AME = +0.267; +1.33 pp por cada 5% de descuento).
  - Sin embargo, otorgar descuentos indiscriminados a segmentos poco reactivos o por canales costosos destruye el margen neto: el subsidio supera el beneficio de la conversión.
- **Perfil del no-convertidor sistemático:**
  - Las quejas de CRM y las devoluciones previas **no explican** estadísticamente la falta de conversión (Mann-Whitney U $p = 0.8038$ y Chi-cuadrado $p = 0.8829$; los clientes insatisfechos convierten al mismo 15.5% que el resto).
  - El problema real es de **fatiga y desalineación de canal**: la tasa de apertura (`open_rate`) de los no-convertidores es de **0.0% mediana vs 66.7%** en convertidores ($p = 3.78 \times 10^{-167}$).
- **El ROI verdadero:** Mientras el ROI naïve medido sobre facturación aparenta ser elevado (~6.8x promedio ponderado), cuando se mide sobre **margen bruto real deduciendo el subsidio del descuento y costos de envío**, el ROI neto de margen colapsa a **0.59x** (destruyendo caja en canales como Social Ads y SMS).

---

## 3. DESENLACE: Plan de Rescate Financiero — Tres Palancas, $395,954 Anuales en Margen

### Recomendación 1: Contención de Devoluciones en Electrónica y Ropa y Calzado
**Responsable:** Operaciones + Gestión de Proveedores

> **"Si implementamos auditorías de calidad a los 5 proveedores críticos de Electrónica y un asistente de recomendación de tallas (biométrico o por historial de compra) en Ropa y Calzado para el canal online, esperamos una reducción del 35% en las devoluciones anómalas de ambas categorías, equivalente a $95,824 anuales en margen operativo recuperado."**

**Justificación cuantitativa:**
- Exceso anualizado en 12 meses = $273,784 ($136,892/semestre).
- Efectividad conservadora del 35% sobre el exceso anómalo: $273,784 \times 0.35 = \mathbf{\$95,824/año}$ ($\$47,912/\text{semestre}$).
- Horizonte de implementación: 60–90 días.

---

### Recomendación 2: Racionalización de Descuentos Inelásticos
**Responsable:** Pricing + Dirección Comercial

> **"Si eliminamos los tramos de descuento superiores al 10% en tienda física y canal online para las SKUs donde el modelo OLS confirma elasticidad nula, esperamos mantener el volumen de ventas actual con una reducción del 60% en el margen cedido por promociones, equivalente a $290,310 anuales en margen bruto directo."**

**Justificación cuantitativa:**
- Costo anual de descuentos = $483,850 ($241,925/semestre).
- Sin elasticidad de demanda, eliminar el 60% del gasto promocional ineficiente transfiere $\mathbf{\$290,310/año}$ ($\$145,155/\text{semestre}$) directamente al margen.
- Piloto recomendado: 30 días en 3 categorías con elasticidad confirmada = 0 antes de escalar.
- Horizonte de implementación: 30 días (piloto) → 90 días (despliegue completo).

---

### Recomendación 3: Reasignación de Marketing hacia Retención Predictiva
**Responsable:** Marketing + BI + CRM

> **"Si reorientamos el presupuesto de campañas masivas por Email hacia canales push segmentados para los 696 clientes Frecuentes/Premium en riesgo de churn temprano, esperamos retener activamente al 50% de los clientes en riesgo, equivalente a $9,820 anuales en margen bruto directo y $39,895 anuales en facturación neta preservada de clientes de alto valor."**

**Justificación cuantitativa:**
- Los 696 clientes en riesgo representan $39,895/semestre en ingresos expuestos y $9,820/semestre en margen bruto directo (`ingreso_esperado_perdido_6m`).
- Una retención activa del 50% preserva $\mathbf{\$4,910/\text{semestre} = \$9,820/\text{año}}$ en margen bruto directo (y $\$19,947/\text{semestre} = \$39,895/\text{año}$ en facturación neta).
- Al suprimir envíos no leídos y campañas de bajo retorno (SMS y Social Ads sin segmentar), se maximiza el ROI neto.
- Horizonte de implementación: 30 días (configuración de triggers predictivos en el DSS).

---

### Resumen Financiero Consolidado

| Palanca | Mecanismo | Impacto Anual Estimado |
|---|---|---|
| Contención de devoluciones anómalas | Auditoría proveedores + recomendador de tallas | **+$95,824** en margen operativo |
| Racionalización de descuentos inelásticos | Eliminar descuentos > 10% sin elasticidad | **+$290,310** en margen bruto directo |
| Marketing de retención predictiva | Campañas trigger push para clientes en riesgo | **+$9,820** en margen (*+$39,895* en ventas brutas) |
| **TOTAL MARGEN OPERATIVO RECUPERABLE** | | **$395,954 anuales** |

> **Comparación:** El margen bruto semestral base actual es $2,155,164. Recuperar $197,977 por semestre ($395,954 anuales) representa un **incremento directo del +9.2% en el margen bruto**, autofinanciado y sin necesidad de aumentar las ventas.

---

## 4. CATÁLOGO DE VISUALIZACIONES EJECUTIVAS (Máx. 10)

> **Regla de diseño:** Cada visualización tiene un título en forma de **insight accionable**, no de descripción. El gráfico prueba el título.

### V1: "Dos categorías concentran el 68% del exceso de devoluciones y drenan $547k de margen operativo"
- **Tipo:** Gráfico de barras horizontales con línea de referencia base (12.6%)
- **Ejes:** Y = Categorías de producto | X = Tasa de devolución (%) y exceso en USD
- **Anotación:** Diferencia en pp vs tasa base y monto de exceso anualizado ($274k/año)
- **Fuente:** `devoluciones_crm/impacto_exceso_por_categoria.csv`
- **Decisión gerencial:** Focalizar la auditoría de calidad en proveedores de Electrónica y el recomendador de tallas para Ropa y Calzado online, no en toda la tienda.

### V2: "El canal digital aporta el 38% de la venta pero sufre una erosión de margen de 4.1 pp por logística inversa"
- **Tipo:** Gráfico de columnas agrupadas con brecha visual y línea de margen post-devoluciones
- **Ejes:** X = Canales (Física, Online, App Móvil) | Y = % Ingreso vs % Margen bruto vs % Margen neto
- **Fuente:** `rentabilidad/margen_por_canal.csv`
- **Decisión gerencial:** Toda política de crecimiento digital debe incorporar una política de devolución más estricta (plazos, penalizaciones por abuso) para no comprar crecimiento de ingreso a costa de destrucción de margen.

### V3: "Los descuentos no generan volumen adicional: elasticidad estadísticamente cero destruye $241k de margen semestral"
- **Tipo:** Forest Plot de coeficientes (con IC95%) del modelo OLS de efectos fijos
- **Ejes:** Y = Tramos de descuento (0-5%, 5-10%, 10-15%, 15-20%, >20%) | X = Efecto estimado en unidades (vs tramo 0%)
- **Nota clave:** Todos los IC95% cruzan el cero → ningún tramo tiene efecto distinguible
- **Fuente:** `descuentos/efecto_volumen_efectos_fijos.csv`
- **Decisión gerencial:** Evidencia suficiente para un piloto de 30 días sin descuentos > 10% en las categorías no elásticas.

### V4: "El 81% del margen descansa en Frecuentes y Premium, pero 696 clientes clave están en riesgo de abandono"
- **Tipo:** Gráfico de dispersión / barras en cuadrante de retención
- **Ejes:** X = Segmento de cliente | Y = Margen acumulado (Frecuente 49.5%, Premium 31.2%) | Tamaño/Detalle = Clientes en riesgo
- **Fuente:** `clv_por_segmento.csv` + `fugas/churn_mayor_valor_en_riesgo.csv`
- **Decisión gerencial:** Reasignar presupuesto de adquisición de nuevos clientes a retención activa de los 696 clientes de alto valor identificados.

### V5: "La conversión de marketing cayó a la mitad (11.7% a 5.1%): la fatiga en Email masivo impulsa el declive"
- **Tipo:** Gráfico de líneas temporal mensual
- **Ejes:** X = Meses (24 meses) | Y = Tasa de conversión mensual por tipo/canal
- **Fuente:** `campanas_marketing` agregado por mes
- **Decisión gerencial:** Detener envíos masivos indiscriminados por Email que han quemado la receptividad de la base de clientes.

### V6: "El descuento en campañas incrementa la conversión pero destruye el retorno neto si no se segmenta quirúrgicamente"
- **Tipo:** Curva sigmoide (probabilidad predicha del modelo logístico multivariado) por segmento
- **Ejes:** X = Descuento ofrecido (0%–30%) | Y = Probabilidad predicha de conversión
- **Fuente:** `marketing/efecto_descuento_logistico.csv`
- **Decisión gerencial:** Emplear descuentos solo en segmentos donde la elasticidad marginal compense el subsidio; eliminar promociones masivas en audiencias inelásticas.

### V7: "Push en App para clientes Premium lidera la conversión (15.3%); Email a Inactivos tiene el menor retorno (4.7%)"
- **Tipo:** Heatmap de rendimiento cruzado (2D grid)
- **Ejes:** Y = Tipo × Canal de campaña | X = Segmento de cliente | Celda = Tasa de conversión (%)
- **Fuente:** `marketing/conversion_combinaciones.csv`
- **Decisión gerencial:** Reasignar el presupuesto de Email a Inactivos hacia App Push para Frecuentes y Premium; son las combinaciones con significancia estadística positiva confirmada.

### V8: "Los no-convertidores no sufren por quejas de CRM (p=0.80), sino por desinterés de apertura (open rate 0% vs 67%)"
- **Tipo:** Gráfico de barras comparativas con intervalos de confianza
- **Grupos:** Comparación de quejas CRM, devoluciones y tasa de apertura entre convertidores y no-convertidores
- **Métrica:** Open rate y p-valores de Mann-Whitney U
- **Fuente:** `marketing/hipotesis_causas_no_conversion.csv` + `marketing/perfil_no_convertidores.csv`
- **Decisión gerencial:** El problema no es fricción post-venta sino fatiga de canal y relevancia de contenido; se debe filtrar por propensión de lectura antes de enviar.

### V9: "El ROI de marketing colapsa de 6.8x bruto a 0.59x sobre margen neto real: medir sobre ventas infla el retorno 11 veces"
- **Tipo:** Gráfico de barras bicolor por tipo de campaña
- **Métricas paralelas:** ROI bruto sobre ventas (barra azul, ~6.8x) | ROI neto de margen deduciendo descuentos y costos operativos (barra verde/roja, 0.59x)
- **Fuente:** `marketing/roi_campanas.csv`
- **Decisión gerencial:** Prohibir el reporte de efectividad de marketing basado en venta bruta; adoptar el ROI sobre margen neto como KPI oficial del área.

### V10: "Intervención de tres palancas recupera $396k anuales en margen (+9.2%) sin necesidad de crecer en ventas"
- **Tipo:** Gráfico Waterfall financiero (cascada semestral en miles USD)
- **Secuencia de barras:**
  1. Margen bruto semestral actual: $2,155,164
  2. + Contención devoluciones (35%): +$47,912
  3. + Racionalización descuentos (60%): +$145,155
  4. + Marketing de retención (50% margen): +$4,910
  5. = Margen semestral post-intervención: **$2,353,141** (+9.19%)
- **Fuente:** `fugas/fugas_impacto_6m.csv` + recomendaciones cuantificadas
- **Decisión gerencial:** El plan de rescate es autofinanciado: los ahorros de la Palanca 2 (descuentos) financian la implementación de las Palancas 1 y 3.

---

## 5. GUIÓN DE DEFENSA ORAL — BANCO DE PREGUNTAS TÉCNICAS

### Pregunta 1: "¿Cómo aseguran que eliminar los descuentos no desplomará las ventas?"
**Respuesta técnica:**
Validamos esto con un modelo de regresión OLS con **efectos fijos por `producto_id`**. Este diseño compara cada producto consigo mismo en períodos con y sin descuento, eliminando el sesgo de que "los mejores productos tienen menos descuentos". El coeficiente estimado para todos los tramos de descuento fue de ≈ 0.01 unidades adicionales con un intervalo de confianza al 95% que incluye el cero (p > 0.15 en todos los tramos). Además, el análisis de balance demostró que los descuentos no llegaron a nuevos compradores, sino a los segmentos Frecuente y Premium que compran de todas formas. La propuesta es un **piloto controlado de 30 días** antes de escalar, para validar con datos reales de este negocio específico.

### Pregunta 2: "¿Las quejas de CRM o las devoluciones explican por qué los clientes no responden a las campañas de marketing?"
**Respuesta técnica:**
Hicimos la prueba formal de hipótesis y la respuesta es **no**. Sometimos los datos al test de Mann-Whitney U para quejas no resueltas y arrojó un p-valor de **0.8038**, mientras que la prueba de Chi-cuadrado para devoluciones previas dio un p-valor de **0.8829**. En ambos casos la hipótesis nula no puede ser rechazada: los clientes con quejas o devoluciones convierten al mismo ritmo (15.5%) que los clientes sin incidencias.
La causa real del fracaso de marketing es la **falta de engagement con el canal**: la tasa de apertura (`open_rate`) de los no-convertidores tiene una mediana de **0.0% frente a 66.7%** en los convertidores ($p = 3.78 \times 10^{-167}$). Los clientes no compran porque ni siquiera abren los correos; saturamos a la audiencia con comunicaciones masivas e irrelevantes.

### Pregunta 3: "¿Cómo calcularon exactamente el exceso de devoluciones?"
**Respuesta técnica:**
Para cada categoría calculamos su tasa de devolución observada. Luego calculamos la **tasa de referencia** = tasa promedio ponderada del resto de las categorías (excluyendo la categoría bajo análisis). Cualquier transacción devuelta por encima de esa tasa base fue clasificada como "exceso anómalo". Multiplicamos ese número de devoluciones en exceso por el ticket medio de devolución de esa categoría para estimar el monto. El escenario reportado es el conservador: asume que la mercancía devuelta no se recupera ($273,784 anuales entre Electrónica y Ropa). Sobre este exceso anual, una contención del 35% aporta exactamente **$95,824 anuales en margen operativo**.

### Pregunta 4: "¿Por qué en marketing el descuento sí tiene efecto, pero en ventas dicen que la elasticidad es cero?"
**Respuesta técnica:**
Son dos mecanismos y dos unidades de análisis totalmente diferentes:
1. En **transacciones (A2)**, el descuento opera sobre el precio de lista de la tienda (física u online). El modelo OLS de efectos fijos demostró que bajar el precio en tienda no genera compras adicionales en unidades (elasticidad volumen ≈ 0).
2. En **campañas de marketing (A4)**, el descuento funciona como un incentivo directo de respuesta (Call to Action). La regresión logística multivariada demostró que un descuento de campaña sí eleva la propensión de conversión ($\beta = +3.285$, $p < 0.001$, AME = +0.267). Sin embargo, el **costo implícito del descuento** deteriora el margen unitario más de lo que compensa la conversión adicional, provocando que el ROI neto de margen colapse a 0.59x si no se segmenta con precisión.

### Pregunta 5: "¿Por qué miden el ROI sobre margen bruto y no sobre facturación?"
**Respuesta técnica:**
Medir el ROI sobre ventas brutas es la **falacia más común del marketing**. Un ejemplo: si una campaña genera $10,000 en ventas de productos con costo de $8,000 que además requerían un descuento de $1,500, la campaña solo generó $500 de margen neto. Si costó $600 operarla (envíos + descuento de campaña), tuvo un **ROI financiero real de -16%**, aunque en términos de venta bruta parezca un éxito de 16x. En BI gerencial, el único ROI relevante es el que mide el flujo de caja neto generado: `(Margen bruto de la compra atribuida - Costo total de la campaña) / Costo total de la campaña`. En RetailVenture, el ROI bruto aparenta ser ~6.8x, pero el ROI neto de margen real es de **0.59x**.

### Pregunta 6: "¿Cómo definieron la métrica de inactividad para el riesgo de churn y qué tan confiable es?"
**Respuesta técnica:**
No definimos un umbral arbitrario de días (ej: "sin comprar en 90 días"). En cambio, estimamos la **curva de supervivencia de Kaplan-Meier** sobre los intervalos entre compras consecutivas de los clientes, segmentada por segmento de cliente. Definimos como "En riesgo" a los clientes cuyo silencio actual de compra lleva a una probabilidad de retorno `S(t) < 0.10`, es decir, que estadísticamente han superado el percentil 90 de su patrón histórico de recompra.
En el **backtest temporal** (entrenado a junio 2024 y evaluado en el segundo semestre de 2024), confirmamos que los clientes catalogados "En riesgo" sufrieron una tasa de no retorno del **26.6%**, en marcado contraste con los clientes sanos (donde el no retorno fue solo del 1.9% en Premium y 10.2% en Frecuentes). Esto demuestra que el indicador captura oportunamente la desaceleración antes de que sea irreversible.

---

## 6. ROADMAP DE IMPLEMENTACIÓN

| Horizonte | Acciones | Responsable | KPI de Seguimiento |
|---|---|---|---|
| **30 días** | Piloto de precios sin descuentos >10% en 2 categorías inelásticas | Pricing | Volumen de unidades vendidas vs período anterior |
| **30 días** | Reconfigurar plataforma de campañas para suprimir envíos con open_rate histórico = 0 | Marketing + TI | Tasa de apertura y costo por conversión |
| **60 días** | Auditoría de proveedores de Electrónica (top 5 por tasa de devolución) | Operaciones | Tasa de devolución mensual de Electrónica |
| **60 días** | Despliegue de campañas push segmentadas para los 696 clientes en riesgo | Marketing | Tasa de reactivación de clientes "En riesgo" |
| **90 días** | Asistente de tallas para Ropa y Calzado en el canal online | Producto Digital | Tasa de devolución de Ropa y Calzado online |
| **90 días** | Revisión de resultados y decisión de escalar el piloto de descuentos | Dirección Comercial | ROI neto de margen de las campañas (nueva métrica oficial) |
