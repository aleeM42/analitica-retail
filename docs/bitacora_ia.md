# Bitácora de Inteligencia Artificial y Criterio Técnico
## Proyecto 01: Retail Intelligence — RetailVenture C.A.
### Asignatura: Tópicos Especiales para la Gestión de Datos

> **Propósito de este documento:** Registrar cada interacción con herramientas de IA generativa, documentando el prompt emitido, la sugerencia recibida y la decisión técnica tomada sobre ella (aceptación, ajuste crítico o rechazo). Este registro demuestra que el equipo **dirige la IA como herramienta**, no que la IA dirige al equipo.
>
> **Principio rector:** Una sugerencia de IA aceptada sin validación técnica independiente es una vulnerabilidad metodológica, no una ventaja. La rúbrica del proyecto penaliza el "vibe coding"; este documento evidencia lo contrario.

---

## Registro de Interacciones

### Sesión 1: Actividad A4 — Diseño del Análisis de Efectividad de Marketing

| Campo | Detalle |
|---|---|
| **Fecha y Fase** | A4: Evaluación de la Efectividad del Marketing |
| **Herramienta** | Claude (Anthropic) vía Antigravity IDE |
| **Prompt emitido** | *"Calcula la correlación entre el descuento ofrecido en las campañas de marketing y la tasa de conversión para determinar si el descuento incentiva la compra."* |
| **Sugerencia de la IA** | La IA generó un cálculo directo de correlación de Pearson entre `descuento_ofrecido` y `convertido`, obteniendo r = 0.31 y concluyendo: *"Existe una correlación positiva moderada: a mayor descuento ofrecido, mayor probabilidad de conversión."* |
| **Decisión** | ❌ **RECHAZADO y reformulado** |
| **Validación técnica** | La correlación de Pearson entre dos variables observacionales sin controles no establece causalidad. El sesgo identificado: los segmentos Premium y Frecuente (que tienen mayor propensión intrínseca a comprar) reciben sistemáticamente más campañas con descuento por decisión del área de marketing. Por lo tanto, la correlación positiva refleja la propensión del segmento, no el efecto del descuento. Esto es un sesgo de variable omitida clásico (omitted variable bias) en el sentido de Angrist & Pischke (2008). |
| **Corrección aplicada** | Se reemplazó por una **Regresión Logística multivariada** con controles fijos para `C(segmento)`, `C(canal_campana)` y `C(tipo_campana)`, con errores estándar robustos HC1. Adicionalmente se calcularon los **Average Marginal Effects** (AME) del descuento para interpretar el impacto en unidades de probabilidad directamente. |
| **Resultado post-corrección** | El coeficiente del descuento no fue estadísticamente distinguible de cero tras controlar por segmento y canal (p > 0.05). Esto es consistente con el hallazgo de A2 (elasticidad precio ≈ 0 en transacciones). La correlación naïve de r = 0.31 era espuria. |

---

### Sesión 2: Actividad A4 — Fórmula de ROI de Campañas de Marketing

| Campo | Detalle |
|---|---|
| **Fecha y Fase** | A4: Cálculo del ROI por tipo de campaña |
| **Herramienta** | Claude (Anthropic) vía Antigravity IDE |
| **Prompt emitido** | *"Genera la fórmula para calcular el ROI de cada tipo de campaña de marketing usando el monto de compra convertida versus el costo del descuento ofrecido."* |
| **Sugerencia de la IA** | La IA propuso: `ROI = (Ventas_Convertidas - Costo_Descuento_Campana) / Costo_Descuento_Campana` e implementó la función directamente sobre `monto_neto` como proxy de ingresos totales de la campaña. |
| **Decisión** | ⚠️ **AJUSTADO CRÍTICAMENTE** |
| **Validación técnica** | El ROI sobre ventas brutas es una **falacia financiera** frecuente en reporting de marketing. El monto de venta bruta no representa el flujo de caja neto generado por la campaña: ignora el costo de los productos vendidos (COGS). Adicionalmente, la fórmula propuesta no incorporó los costos operativos de envío del canal. Un ejemplo numérico para evidenciar el error: una campaña de Email que genera $10,000 en ventas de productos con costo de $8,000 y un descuento de campaña de $1,500 aparece como ROI de 5.67x en la fórmula propuesta, pero el ROI real sobre margen es negativo: ($1,000 margen - $1,500 descuento - $25 envío) / ($1,500 + $25) = **-33.8%**. |
| **Corrección aplicada** | Se implementaron **dos perspectivas de ROI** para el reporte: (1) `ROI_bruto` basado en monto de venta (como referencia histórica del equipo de marketing); (2) `ROI_neto_margen` = `(Margen_bruto_atribuido - Costo_descuento_campana - Costo_envio_canal) / (Costo_descuento_campana + Costo_envio_canal)`. Solo el ROI neto se usa en las recomendaciones ejecutivas. Los costos de envío por canal se parametrizaron según estándares del sector (Email: $0.005, App Push: $0.002, SMS: $0.025 por impacto). |
| **Resultado post-corrección** | El ROI neto de margen reveló que varias campañas consideradas "exitosas" por el área de marketing tenían ROI < 1.0x cuando se medía correctamente. Esto fundamenta la Recomendación 3 del storytelling ejecutivo. |

---

### Sesión 3: Actividad A4 — Identificación de Clientes No Convertidores

| Campo | Detalle |
|---|---|
| **Fecha y Fase** | A4.3: Perfilado de no-convertidores e hipótesis causales |
| **Herramienta** | Claude (Anthropic) vía Antigravity IDE |
| **Prompt emitido** | *"Identifica cuáles son los clientes que reciben campañas pero no compran, y lista sus características demográficas promedio."* |
| **Sugerencia de la IA** | La IA generó un análisis descriptivo: segmento modal, ciudad más frecuente y edad promedio de los no-convertidores, sin ninguna prueba estadística que validara si las diferencias eran significativas o producto del azar. Concluía: *"Los no-convertidores son principalmente del segmento Esporádico, de la ciudad de Valencia, con edad promedio de 34 años."* |
| **Decisión** | ⚠️ **AJUSTADO con pruebas estadísticas** |
| **Validación técnica** | Las diferencias en promedios o proporciones entre grupos sin pruebas de hipótesis son anecdóticas. Si el segmento Esporádico tiene mayor proporción en no-convertidores, puede ser simplemente porque es el segmento más numeroso en la base. Sin una prueba Chi-cuadrado o Mann-Whitney U con p-valor, no se puede afirmar que la diferencia es estadísticamente significativa vs el azar muestral. La rúbrica del proyecto penaliza correlaciones sin investigar causalidad; este tipo de análisis descriptivo sin validación estadística caería en esa penalización. |
| **Corrección aplicada** | Se reemplazó el análisis descriptivo por: (1) **Test Mann-Whitney U** para variables continuas (quejas no resueltas, monto devuelto, open rate, edad); (2) **Chi-cuadrado** para variables categóricas (presencia de quejas, historial de devoluciones); (3) Formulación explícita de tres **hipótesis causales** (H1, H2, H3) con su estadístico, p-valor y clasificación de "Confirmada/No confirmada". |
| **Resultado post-corrección** | Las tres hipótesis se evaluaron con rigor. El resultado (confirmación o rechazo estadístico) es trazable y defendible ante preguntas de escrutinio técnico en la defensa oral. |

---

### Sesión 4: Actividad A5 — Selección de Visualizaciones para el Dashboard

| Campo | Detalle |
|---|---|
| **Fecha y Fase** | A5: Diseño del dashboard ejecutivo |
| **Herramienta** | Claude (Anthropic) vía Antigravity IDE |
| **Prompt emitido** | *"Sugiere visualizaciones para un dashboard completo de retail que muestre los resultados del proyecto."* |
| **Sugerencia de la IA** | La IA propuso 15 gráficos estándar de retail: pastel de participación de ventas por categoría, barras de clientes por ciudad, líneas de ventas mensuales, treemap de SKUs, mapa de calor de horarios de compra, etc. Todos con títulos descriptivos como "Ventas por Categoría" o "Evolución de Clientes". |
| **Decisión** | ❌ **RECHAZADO en su totalidad y rediseñado** |
| **Validación técnica** | El enunciado del proyecto es explícito: **máximo 10 visualizaciones**, y cada una debe tener un **título en forma de insight accionable**, no de descripción. Un gráfico de "Ventas por categoría" describe datos; no prueba ninguna tesis, no responde ninguna pregunta gerencial y no orienta ninguna decisión. Los 15 gráficos sugeridos eran visualizaciones decorativas de BI básico, no visualizaciones analíticas de storytelling. Adicionalmente, la rúbrica valora el poder explicativo sobre la cantidad. Incluir 15 gráficos cuando el límite es 10 evidenciaría que no se leyó el enunciado. |
| **Corrección aplicada** | Se diseñó un catálogo de exactamente **10 visualizaciones**, cada una: (a) con un título que formula una tesis o hallazgo accionable; (b) con una fuente de datos específica del proyecto; (c) con un valor explicativo claro que orienta una decisión gerencial concreta; (d) ordenadas narrativamente siguiendo la estructura Inicio → Nudo → Desenlace del storytelling. |
| **Resultado post-corrección** | Las 10 visualizaciones forman una narrativa coherente que lleva al espectador desde el diagnóstico hasta el plan de acción cuantificado. Cada visualización prueba un hallazgo específico del análisis estadístico realizado en A1–A4. |

---

### Sesión 5: Actividad A5 — Cuantificación de Recomendaciones

| Campo | Detalle |
|---|---|
| **Fecha y Fase** | A5: Formulación de recomendaciones ejecutivas |
| **Herramienta** | Claude (Anthropic) vía Antigravity IDE |
| **Prompt emitido** | *"Genera tres recomendaciones estratégicas para mejorar los resultados de RetailVenture basadas en el análisis."* |
| **Sugerencia de la IA** | La IA generó: (1) "Mejorar la experiencia de devoluciones para reducir la insatisfacción del cliente"; (2) "Optimizar la estrategia de descuentos para maximizar el valor"; (3) "Aumentar las ventas en un 15% mediante campañas más efectivas". |
| **Decisión** | ❌ **RECHAZADO en su totalidad y reformulado desde cero** |
| **Validación técnica** | Las recomendaciones propuestas son vagas, genéricas y no cuantificadas. El enunciado del proyecto exige explícitamente la siguiente sintaxis: *"Si hacemos X, esperamos un incremento/reducción de Y% en Z métrica, equivalente a [monto] en ingresos/margen."* Las sugerencias de la IA no cumplen ninguno de esos tres requisitos: no especifican la acción concreta (X), no cuantifican el impacto esperado (Y% en Z) y no expresan el equivalente monetario. Adicionalmente, "aumentar las ventas un 15%" no está fundamentado en ningún análisis estadístico del proyecto. |
| **Corrección aplicada** | Se reformularon las tres recomendaciones desde los datos reales: cada una especifica (a) la acción concreta a implementar; (b) el porcentaje de mejora esperado respaldado por el cálculo estadístico (ej: 35% de reducción en exceso de devoluciones); (c) el monto equivalente en USD calculado directamente de los resultados de los análisis (ej: $191,648 anuales). La justificación matemática de cada monto está documentada en `presentacion_ejecutiva.md`. |
| **Resultado post-corrección** | Las tres recomendaciones son auditables: cualquier miembro del jurado puede verificar los números siguiendo la cadena: CSV de resultados → fórmula aplicada → monto reportado. Impacto total consolidado: **$580,358 anuales** en margen operativo recuperable. |

---

### Sesión 6: Actividad A4 — Especificación Econométrica y Multicolinealidad Estructural

| Campo | Detalle |
|---|---|
| **Fecha y Fase** | A4.2: Especificación del modelo logístico multivariado |
| **Herramienta** | Claude (Anthropic) vía Antigravity IDE |
| **Prompt emitido** | *"Construye la fórmula de regresión logística controlando simultáneamente por segmento, canal de envío y tipo de campaña."* |
| **Sugerencia de la IA** | La IA propuso: `convertido ~ descuento_ofrecido + C(segmento) + C(canal_campana) + C(tipo_campana)` con errores robustos HC1. |
| **Decisión** | ⚠️ **AJUSTADO CRÍTICAMENTE (Corrección de rango defectuoso)** |
| **Validación técnica** | Al estimar el modelo, la matriz hessiana resultó singular (`LinAlgError: Singular matrix`). El análisis de álgebra lineal reveló una **dependencia lineal exacta (Dummy Variable Trap)**: en el diseño de datos de RetailVenture, cada `tipo_campana` está unívocamente determinado por su `canal_campana` (`push_reactivacion` solo existe en `push_app`, `sms_oferta_flash` solo en `sms`, `social_ads` solo en `redes_sociales`). Incluir ambos factores categóricos introdujo tres columnas linealmente dependientes en la matriz de diseño $X$, violando el supuesto de rango completo ($rank(X) < k$). |
| **Corrección aplicada** | Se removió el término redundante `C(canal_campana)` manteniendo `C(tipo_campana)` (que tiene mayor granularidad, ya que además discrimina `email_descuento` de `email_fidelizacion` dentro del canal de email). Se estimó con errores robustos HC1 y se validó la convergencia del algoritmo MLE en 7 iteraciones. |
| **Resultado post-corrección** | Convergencia numérica garantizada, errores estándar robustos válidos y cálculo de efectos marginales promedio (AME) completado sin advertencias ni singularidad. |

---

## Resumen Ejecutivo de la Bitácora

| Sesión | Fase | Herramienta | Tipo de Decisión | Impacto en la Calidad del Análisis |
|---|---|---|---|---|
| 1 | A4.2 Efecto del descuento en conversión | Claude | ❌ Rechazado y reformulado | Evitó publicar una correlación espuria como causalidad; resultado estadísticamente más robusto |
| 2 | A4.4 ROI de campañas | Claude | ⚠️ Ajustado críticamente | Evitó sobreestimar el retorno de marketing; el ROI correcto es 4x menor al reportado naïvemente |
| 3 | A4.3 Perfil de no-convertidores | Claude | ⚠️ Ajustado con validación estadística | Evitó conclusiones anecdóticas; se añadieron 3 hipótesis con pruebas formales |
| 4 | A5 Selección de gráficos | Claude | ❌ Rechazado y rediseñado | Evitó superar el límite de 10 visualizaciones con gráficos decorativos sin valor analítico |
| 5 | A5 Recomendaciones | Claude | ❌ Rechazado y reformulado | Evitó recomendaciones genéricas; se produjeron 3 recomendaciones cuantificadas y auditables |
| 6 | A4.2 Multicolinealidad en logit | Claude | ⚠️ Ajustado críticamente | Identificó y corrigió trampa de dummies estructural; garantizó convergencia MLE y errores HC1 |

**Tasa de aceptación directa de sugerencias de IA: 0/6 (0%)** — Todas requirieron ajuste crítico o fueron rechazadas y reformuladas desde fundamentos estadísticos, econométricos y de negocio propios.

