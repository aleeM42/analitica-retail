# Retail Intelligence: Márgenes en Crisis — El Plan de Rescate
## RetailVenture C.A. | Presentación Ejecutiva de Resultados
### Tópicos Especiales para la Gestión de Datos | Semana 15

---

## ESTRUCTURA DE LA PRESENTACIÓN (15 minutos)

| Bloque | Tiempo | Contenido |
|---|---|---|
| **Inicio** | 0:00–3:00 | Diagnóstico: los tres síntomas y la pregunta central |
| **Nudo** | 3:00–8:00 | Los cuatro frentes de fuga de ingresos con evidencia estadística |
| **Desenlace** | 8:00–11:30 | Plan de intervención: tres recomendaciones cuantificadas |
| **Escrutinio** | 11:30–15:00 | Sesión de preguntas técnicas y de negocio |

---

## 1. INICIO: El Espejismo del Crecimiento y la Crisis Silenciosa

> **Apertura ejecutiva:**
> RetailVenture C.A. cumple 12 años liderando el retail omnicanal en Venezuela. En los últimos 24 meses facturó **$17,392,987** y sus sistemas procesan 50,000 transacciones con 318 productos en tres canales. Los números absolutos parecen sólidos. Pero las tendencias operativas cuentan otra historia.

### Los Tres Síntomas de Alarma

| Indicador | Valor Actual | Tendencia | Impacto |
|---|---|---|---|
| Ticket promedio | Caída del **8% interanual** | ↓ Acelerada | Erosión de ingresos por cliente |
| Tasa de devoluciones | **14%** (Q4) | ↑ Creciente | Destrucción de margen y logística |
| Conversión de marketing | **11%** (vs 22% hace 18 meses) | ↓ Mitad en 18 meses | Desperdicio masivo de presupuesto |

### La Pregunta Gerencial Central

> *¿Es una contracción generalizada del consumo en Venezuela… o un problema de gestión interna que podemos resolver?*

**La respuesta de los datos: es un problema interno.** Identificamos cuatro fuentes de fuga cuantificadas que suman **$521,853 anuales** en margen recuperable. Ninguna requiere más ventas para solucionarse; requieren decisiones quirúrgicas.

---

## 2. NUDO: Los Cuatro Frentes de Fuga de Ingresos

### Fuga #1: La Hemorragia Localizada en Devoluciones — **$547,567 en 24 meses**

- La tasa global de devoluciones es 13.45%, pero el problema **no es general**.
- Dos categorías concentran todo el exceso anómalo estadísticamente confirmado:

| Categoría | Tasa de Devolución | Tasa de Referencia (resto) | Exceso en 24 meses |
|---|---|---|---|
| **Ropa y Calzado** | **21.78%** | 11.79% | $147,249 |
| **Electrónica** | **17.65%** | 12.60% | $400,318 |
| **Total Exceso** | — | — | **$547,567** |

- **Dimensión canal:** El canal Online factura el 37.6% de los ingresos pero su margen tras devoluciones es de apenas **9.5%** (vs 13.7% en tienda física), revelando una destrucción de 3.0 pp por logística inversa mal gestionada.

### Fuga #2: La Falsa Salvación de los Descuentos — **$483,850 en 12 meses**

- El sistema aplicó $967,700 en descuentos totales en los 24 meses del dataset ($483,850/año, $241,925/semestre).
- **El hallazgo estadístico clave:** Modelo OLS con efectos fijos por `producto_id` (el mismo producto comparado consigo mismo con y sin descuento) entrega un **coeficiente de elasticidad de ~0** (IC 95% incluye cero, p > 0.15).
- **Conclusión:** Los descuentos no generan volumen incremental. Se subsidia a clientes que habrían comprado de todas formas al precio de lista.
- El techo del daño recuperable: **$241,925/semestre** si se eliminan los descuentos sin efecto en volumen.

### Fuga #3: Erosión Silenciosa de Clientes de Alto Valor — **$39,895 en riesgo semestral**

- Los segmentos Frecuente y Premium concentran el **92% del margen bruto total**.
- El modelo de supervivencia Kaplan-Meier por intervalos entre compras identificó **696 clientes** en estado "En riesgo" (silencio de compra que supera el percentil 90 de su patrón histórico, S(t) < 0.10).
- Pérdida esperada proyectada a 6 meses: **$39,895** (escenario severo: hasta $293,000).
- El backtest del modelo (datos hasta junio 2024, validado contra jul-dic 2024) confirmó una tasa de no retorno real del 87% en el segmento "En riesgo".

### Fuga #4: Desconexión y Desperdicio en Marketing — ROI Real vs ROI Aparente

- La tasa de conversión global colapsó del 22% al 11% en 18 meses.
- **Análisis causal (Regresión Logística multivariada):** Controlando por segmento, canal y tipo de campaña, el coeficiente del descuento ofrecido sobre la probabilidad de conversión no es estadísticamente distinguible de cero (p > 0.05 después de controles).
- **Perfil del no-convertidor sistemático:** Los clientes que reciben campañas pero no convierten tienen:
  - Mayor carga de quejas no resueltas en CRM.
  - Mayor historial de devoluciones previas.
  - Menor tasa de apertura de mensajes (señal de desalineación canal-segmento).
- **El ROI verdadero:** Cuando se calcula sobre margen bruto real (no venta bruta), el ROI de varias campañas colapsa de cifras aparentemente positivas a valores cercanos a 1.1x o negativos.

---

## 3. DESENLACE: Plan de Rescate Financiero — Tres Palancas, $521,853 Anuales

### Recomendación 1: Contención de Devoluciones en Electrónica y Ropa y Calzado
**Responsable:** Operaciones + Gestión de Proveedores

> **"Si implementamos auditorías de calidad a los 5 proveedores críticos de Electrónica y un asistente de recomendación de tallas (biométrico o por historial de compra) en Ropa y Calzado para el canal online, esperamos una reducción del 35% en las devoluciones anómalas de ambas categorías, equivalente a $191,648 anuales en margen operativo recuperado."**

**Justificación cuantitativa:**
- Exceso anual = $273,783 ($136,892/semestre).
- Efectividad conservadora del 35% sobre el exceso → $95,824/semestre recuperados = **$191,648/año**.
- Horizonte de implementación: 60–90 días.

---

### Recomendación 2: Racionalización de Descuentos Inelásticos
**Responsable:** Pricing + Dirección Comercial

> **"Si eliminamos los tramos de descuento superiores al 10% en tienda física y canal online para las SKUs donde el modelo OLS confirma elasticidad nula, esperamos mantener el volumen de ventas actual con una reducción del 60% en el margen cedido por promociones, equivalente a $290,310 anuales en margen bruto directo."**

**Justificación cuantitativa:**
- Costo anual de descuentos = $483,850.
- Sin elasticidad de demanda, eliminar el 60% del gasto ineficiente transfiere $290,310 directamente al margen.
- Piloto recomendado: 30 días en 3 categorías con elasticidad confirmada = 0 antes de escalar.
- Horizonte de implementación: 30 días (piloto) → 90 días (despliegue completo).

---

### Recomendación 3: Reasignación de Marketing hacia Retención Predictiva
**Responsable:** Marketing + BI + CRM

> **"Si reorientamos el presupuesto de campañas masivas por Email hacia canales push segmentados para los 696 clientes Frecuentes/Premium en riesgo de churn, y pausamos envíos a clientes con quejas CRM activas no resueltas, esperamos retener al 50% de los clientes en riesgo, equivalente a $39,895 anuales en ingresos netos preservados de clientes de alto valor."**

**Justificación cuantitativa:**
- Los 696 clientes en riesgo representan $39,895/semestre en ingresos en peligro (`ingreso_esperado_perdido_6m`).
- Una retención activa del 50% de ellos preserva **~$19,947/semestre = $39,895/año** en ingresos directos.
- La mejora en la tasa de conversión reduce también el costo por conversión, mejorando el ROI neto de margen.
- Horizonte de implementación: 30 días (configuración de triggers predictivos en el DSS).

---

### Resumen Financiero Consolidado

| Palanca | Mecanismo | Impacto Anual Estimado |
|---|---|---|
| Contención de devoluciones anómalas | Auditoría proveedores + recomendador de tallas | **+$191,648** en margen |
| Racionalización de descuentos inelásticos | Eliminar descuentos > 10% sin elasticidad | **+$290,310** en margen |
| Marketing de retención predictiva | Campañas trigger + pausa a insatisfechos | **+$39,895** en ingresos preservados |
| **TOTAL RECUPERABLE** | | **$521,853 anuales** |

> **Comparación:** El margen bruto total de 24 meses fue $4,310,329. Recuperar $521k anuales = **+12.1% de mejora en el margen bruto semestral actual**, sin necesidad de crecer en ventas.

---

## 4. CATÁLOGO DE VISUALIZACIONES EJECUTIVAS (Máx. 10)

> **Regla de diseño:** Cada visualización tiene un título en forma de **insight accionable**, no de descripción. El gráfico prueba el título.

### V1: "Dos categorías concentran el 68% del exceso de devoluciones y drenan $547k de margen operativo"
- **Tipo:** Gráfico de barras horizontales con línea de referencia base (12.6%)
- **Ejes:** Y = Categorías de producto | X = Tasa de devolución (%) y exceso en USD
- **Anotación:** Diferencia en pp vs tasa base y monto de exceso anualizado
- **Fuente:** `devoluciones_crm/impacto_exceso_por_categoria.csv`
- **Decisión gerencial:** Focalizar la auditoría de calidad en proveedores de Electrónica y el recomendador de tallas para Ropa y Calzado online, no en toda la tienda.

### V2: "El canal digital aporta el 38% de la venta pero sufre una erosión de margen de 3.0 pp por logística inversa"
- **Tipo:** Gráfico de columnas agrupadas con brecha visual y línea de margen post-devoluciones
- **Ejes:** X = Canales (Física, Online, App Móvil) | Y = % Ingreso vs % Margen bruto vs % Margen neto
- **Fuente:** `rentabilidad/margen_por_canal.csv`
- **Decisión gerencial:** Toda política de crecimiento digital debe incorporar una política de devolución más estricta (plazos, penalizaciones por abuso) para no seguir comprando crecimiento de ingreso a costa de destrucción de margen.

### V3: "Los descuentos no generan volumen adicional: elasticidad estadísticamente cero destruye $241k de margen semestral"
- **Tipo:** Forest Plot de coeficientes (con IC95%) del modelo OLS de efectos fijos
- **Ejes:** Y = Tramos de descuento (0-5%, 5-10%, 10-15%, 15-20%, >20%) | X = Efecto estimado en unidades (vs tramo 0%)
- **Nota clave:** Todos los IC95% cruzan el cero → ningún tramo tiene efecto distinguible
- **Fuente:** `descuentos/efecto_volumen_efectos_fijos.csv`
- **Decisión gerencial:** Evidencia suficiente para un piloto de 30 días sin descuentos > 10% en las categorías no elásticas.

### V4: "El 92% del margen descansa en Frecuentes y Premium, pero 696 clientes clave están en riesgo de abandono inmediato"
- **Tipo:** Gráfico de dispersión / burbujas en cuadrante de retención
- **Ejes:** X = Días desde última compra (recencia) | Y = Margen histórico acumulado | Color = Estado churn | Tamaño = CLV estimado
- **Fuente:** `clv_por_segmento.csv` + `fugas/churn_mayor_valor_en_riesgo.csv`
- **Decisión gerencial:** Reasignar presupuesto de adquisición de nuevos clientes a retención activa de los 696 identificados.

### V5: "La conversión de marketing colapsó un 50% en 18 meses: el Email masivo es el principal responsable"
- **Tipo:** Gráfico de líneas temporal (eje temporal en meses)
- **Ejes:** X = Meses (24 meses) | Y = Tasa de conversión mensual por canal de campaña
- **Fuente:** `marketing/conversion_combinaciones.csv` (agregado por mes y canal)
- **Decisión gerencial:** Identificar en qué mes comenzó la caída y correlacionarla con cambios en la estrategia de envíos para confirmar la causa raíz.

### V6: "Ofrecer más descuento en campañas no mejora la conversión: la curva logística se aplana pasado el 5%"
- **Tipo:** Curva sigmoide (probabilidad predicha del modelo logístico) por segmento
- **Ejes:** X = Descuento ofrecido (0%–30%) | Y = Probabilidad predicha de conversión
- **Fuente:** `marketing/efecto_descuento_logistico.csv` (valores predichos del modelo)
- **Decisión gerencial:** Fijar el descuento de campaña máximo en 5-8% en segmentos sensibles; eliminar los >15% que consumen margen sin retorno adicional.

### V7: "Push en App para clientes Premium logra la mayor conversión; Email a Inactivos es el peor uso del presupuesto"
- **Tipo:** Heatmap de rendimiento cruzado (2D grid)
- **Ejes:** Y = Tipo × Canal de campaña | X = Segmento de cliente | Celda = Tasa de conversión (%)
- **Fuente:** `marketing/conversion_combinaciones.csv`
- **Decisión gerencial:** Reasignar el presupuesto de Email masivo a Inactivos hacia App Push para Frecuentes y Premium; son las combinaciones con significancia estadística positiva confirmada.

### V8: "Los clientes con quejas abiertas convierten a una tasa 75% menor: marketing falla porque CRM falla primero"
- **Tipo:** Gráfico de barras comparativas con intervalos de confianza
- **Grupos:** Sin quejas vs Con quejas no resueltas | Sin devoluciones recientes vs Con devoluciones
- **Métrica:** Tasa de conversión de campañas y p-valor del Mann-Whitney U
- **Fuente:** `marketing/perfil_no_convertidores.csv`
- **Decisión gerencial:** Antes de enviar una campaña, el sistema debe verificar el estado CRM del cliente y excluirlo del envío si tiene quejas no resueltas > SLA (72h).

### V9: "El ROI de marketing colapsa de 4.2x a 1.1x cuando se mide sobre margen neto: el rendimiento real es 4 veces menor"
- **Tipo:** Gráfico de barras bicolor / Waterfall por tipo de campaña
- **Métricas paralelas:** ROI bruto (barra azul) | ROI neto de margen incluyendo costo de envío (barra naranja)
- **Fuente:** `marketing/roi_campanas.csv`
- **Decisión gerencial:** Prohibir el reporte de efectividad de marketing basado en venta bruta; adoptar el ROI sobre margen neto como KPI oficial del área.

### V10: "Intervención estratégica de tres palancas recupera $521k anuales sin necesidad de crecer en ventas"
- **Tipo:** Gráfico Waterfall financiero (cascada)
- **Secuencia de barras:**
  1. Margen bruto semestral actual: $2,155,164
  2. + Contención devoluciones: +$95,824
  3. + Racionalización descuentos: +$145,155
  4. + Marketing de retención: +$19,947
  5. = Margen proyectado post-intervención: **$2,416,090** (+12.1%)
- **Fuente:** `fugas/fugas_impacto_6m.csv` + recomendaciones cuantificadas
- **Decisión gerencial:** El plan de rescate es autofinanciado: los ahorros de la Palanca 2 (descuentos) financian la implementación de las Palancas 1 y 3.

---

## 5. GUIÓN DE DEFENSA ORAL — BANCO DE PREGUNTAS TÉCNICAS

### Pregunta 1: "¿Cómo aseguran que eliminar los descuentos no desplomará las ventas?"
**Respuesta técnica:**
Validamos esto con un modelo de regresión OLS (Mínimos Cuadrados Ordinarios) con **efectos fijos por `producto_id`**. Este diseño compara cada producto consigo mismo en períodos con y sin descuento, eliminando el sesgo de que "los mejores productos tienen menos descuentos". El coeficiente estimado para todos los tramos de descuento fue de ≈ 0.01 unidades adicionales con un intervalo de confianza al 95% que incluye el cero (p > 0.15 en todos los tramos). Además, el análisis de balance demostró que los descuentos no llegaron a nuevos compradores, sino a los segmentos Frecuente y Premium que compran de todas formas. La propuesta es un **piloto controlado de 30 días** antes de escalar, para validar con datos reales de este negocio específico.

### Pregunta 2: "¿Por qué dicen que las quejas de CRM no afectan las ventas pero sí afectan el marketing?"
**Respuesta técnica:**
Son dos efectos distintos sobre dos métricas distintas. El análisis pre-post de la **frecuencia de compra** antes y después de una interacción CRM mostró que el intervalo de confianza de la diferencia en compras incluye el cero: los clientes con quejas no resueltas no compraron menos en el mes siguiente. Eso es coherente con el sector retail: el cliente no abandona inmediatamente, especialmente si no tiene alternativas fáciles.

Pero la **receptividad a las campañas de marketing** es otra historia. Cuando cruzamos el perfil de no-convertidores con el historial CRM, encontramos que los clientes con quejas abiertas tienen una tasa de conversión 75% menor (confirmado estadísticamente con Mann-Whitney U, p < 0.05). El mecanismo: el cliente con una queja abierta **abre el email** pero no compra porque la fricción emocional bloquea la decisión. Eso explica que la frecuencia de compra no caiga (compra por necesidad en otros canales) pero la respuesta a campañas sí colapsa.

### Pregunta 3: "¿Cómo calcularon exactamente el exceso de devoluciones?"
**Respuesta técnica:**
Para cada categoría calculamos su tasa de devolución observada. Luego calculamos la **tasa de referencia** = tasa promedio ponderada del resto de las categorías (excluyendo la categoría bajo análisis). Cualquier transacción devuelta por encima de esa tasa base fue clasificada como "exceso anómalo". Multiplicamos ese número de devoluciones en exceso por el ticket medio de devolución de esa categoría para estimar el monto. El escenario reportado es el conservador: asume que la mercancía devuelta no se recupera. El escenario optimista (mercancía revendida al costo) está también disponible en los datos y reduce el impacto un 40%.

### Pregunta 4: "¿Qué modelo estadístico usaron para el efecto del descuento en marketing y por qué ese y no otro?"
**Respuesta técnica:**
Usamos una **regresión logística multivariada** con la variable dependiente `convertido` (0/1) y los siguientes controles simultáneos: `C(segmento)`, `C(canal_campana)` y `C(tipo_campana)`. Los errores estándar son HC1 (robustos a heterocedasticidad). Elegimos logística porque la variable objetivo es binaria y la logística preserva que las probabilidades predichas estén entre 0 y 1. La alternativa (correlación de Pearson o OLS con variable binaria) daría predicciones fuera del rango [0,1] y sería técnicamente incorrecta. Reportamos tanto los Odds Ratios (para interpretación multiplicativa del efecto) como los **Average Marginal Effects** (para interpretación en unidades de probabilidad directamente legibles por la gerencia).

### Pregunta 5: "¿Por qué miden el ROI sobre margen bruto y no sobre facturación?"
**Respuesta técnica:**
Medir el ROI sobre ventas brutas es la **falacia más común del marketing**. Un ejemplo: si una campaña genera $10,000 en ventas de productos con costo de $8,000 que además requerían un descuento de $1,500, la campaña solo generó $500 de margen neto. Si costó $600 operarla (envíos + descuento de campaña), tuvo un **ROI financiero real de -16%**, aunque en términos de venta bruta parezca un éxito de 16x. En BI gerencial, el único ROI relevante es el que mide el flujo de caja neto generado: `(Margen bruto de la compra atribuida - Costo total de la campaña) / Costo total de la campaña`.

### Pregunta 6: "¿Cómo definieron la métrica de inactividad para el riesgo de churn?"
**Respuesta técnica:**
No definimos un umbral arbitrario de días (ej: "sin comprar en 90 días"). En cambio, estimamos la **curva de supervivencia de Kaplan-Meier** sobre los intervalos entre compras consecutivas de los clientes, segmentada por segmento de cliente. Esta curva modela la probabilidad de que un cliente que lleva N días sin comprar realmente vuelva a comprar. Definimos como "En riesgo" a los clientes cuyo silencio actual de compra lleva a una probabilidad de retorno `S(t) < 0.10`, es decir, que estadísticamente han superado el percentil 90 de su patrón histórico de recompra. Esto hace el umbral específico a la cadencia real del segmento, no una regla igual para todos.

---

## 6. ROADMAP DE IMPLEMENTACIÓN

| Horizonte | Acciones | Responsable | KPI de Seguimiento |
|---|---|---|---|
| **30 días** | Piloto de precios sin descuentos >10% en 2 categorías | Pricing | Volumen de unidades vendidas vs período anterior |
| **30 días** | Configurar filtro CRM en la plataforma de campañas (pausa envíos a clientes con quejas activas) | Marketing + TI | Tasa de apertura y conversión de la campaña filtrada |
| **60 días** | Auditoría de proveedores de Electrónica (top 5 por tasa de devolución) | Operaciones | Tasa de devolución mensual de Electrónica |
| **60 días** | Despliegue de campañas push segmentadas para los 696 clientes en riesgo | Marketing | Tasa de reactivación de clientes "En riesgo" |
| **90 días** | Asistente de tallas para Ropa y Calzado en el canal online | Producto Digital | Tasa de devolución de Ropa y Calzado online |
| **90 días** | Revisión de resultados y decisión de escalar el piloto de descuentos | Dirección Comercial | ROI neto de margen de las campañas (nueva métrica oficial) |
