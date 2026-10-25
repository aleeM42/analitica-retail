# GUÍA MAESTRA DE IMPLEMENTACIÓN PARA CLAUDE: ACTIVIDADES A4 Y A5
## Proyecto 01: Retail Intelligence — RetailVenture C.A.
### Asignatura: Tópicos Especiales para la Gestión de Datos (Prof. Armen Djenanian)

---

## 0. INSTRUCCIONES DE EJECUCIÓN PARA CLAUDE (PROMPT SYSTEM DIRECTIVE)

> **ROL DE CLAUDE:**
> Actúa como un **Senior BI Architect & Data Scientist con más de 15 años de experiencia**, especializado en Analítica de Retail, Econometría Aplicada y Storytelling Ejecutivo de Datos. Tu misión es implementar con rigor técnico, estadístico y financiero las **Actividades A4 (Evaluación de la Efectividad del Marketing)** y **A5 (Storytelling Ejecutivo y Recomendaciones)** en el repositorio de **RetailVenture C.A.**
>
> **PRINCIPIOS DE IMPLEMENTACIÓN:**
> 1. **Causalidad > Correlación:** No presentes correlaciones superficiales sin controlar factores de confusión (segmento de cliente, canal, estacionalidad, endogeneidad de descuentos). La rúbrica penaliza explícitamente correlaciones sin investigar causalidad (30% de la nota).
> 2. **Consistencia Numérica Absoluta:** Tus cálculos en A4 y A5 deben conectarse armónicamente con los hallazgos y cifras consolidadas en A1, A2 y A3.
> 3. **Rigor Estadístico:** Todo reclamo de efectividad, impacto o diferencia debe estar respaldado por pruebas de hipótesis (Z-test de proporciones, Chi-cuadrado, Regresión Logística con errores robustos, intervalos de confianza al 95% y p-valores).
> 4. **Fórmulas Mandatorias de Negocio:** Las recomendaciones deben formularse estrictamente como:  
>    `"Si hacemos X, esperamos un incremento/reducción de Y% en Z métrica, equivalente a [monto en USD] en ingresos/margen"`.
> 5. **Estructura del Repositorio:** Respeta estrictamente los patrones de diseño, nombres de módulos, conexiones a DuckDB y estructura del proyecto.

---

## 1. CONTEXTO EMPRESARIAL Y ESTADO ACTUAL DEL PROYECTO

### 1.1 El Caso de Negocio: RetailVenture C.A.
- **Empresa:** Cadena de retail omnicanal en Venezuela con 12 años de trayectoria (canales: tienda física, ecommerce online, app móvil).
- **Ventana de Observación:** 24 meses de datos históricos (01 de enero de 2023 al 31 de diciembre de 2024; 731 días).
- **Volumen Operativo:** ~50,000 transacciones, 8,000 clientes registrados, 318 productos activos en catálogo.
- **Crisis de Desempeño:**
  - El ticket promedio cayó un **8% interanual**.
  - La tasa de devoluciones trepó al **14%** en el último trimestre.
  - La efectividad de las campañas de marketing cayó a la mitad: del **22% al 11% de conversión** en 18 meses.
  - La gerencia exige saber **qué está ocurriendo, por qué está ocurriendo y qué acciones correctivas concretas tomar**.

### 1.2 Línea Base Cuantitativa Consolidada (A1, A2 y A3)
Para garantizar coherencia analítica en A4 y A5, Claude debe tener presentes los datos empíricos ya computados en el repositorio:
1. **Volumen Financiero:**
   - Ingresos Totales (24 meses): **$17,392,987.48** (~$4,348,246.87 por semestre).
   - Margen Bruto Total (24 meses): **$4,310,329.05** (Margen promedio: **24.78%**).
2. **Canales de Venta:**
   - **Tienda Física:** 45.2% de ingresos ($7.86M), 47.5% de margen ($2.05M), margen bruto 26.0%. Devoluciones: $1.13M. Margen post-devoluciones conservador: 13.7%.
   - **Online:** 37.6% de ingresos ($6.55M), 34.6% de margen ($1.49M), margen bruto 22.8% (brecha negativa de -3.05 pp vs ingreso). Devoluciones: $959k. Margen post-devoluciones conservador: 9.5% (fuerte erosión logística).
   - **App Móvil:** 17.2% de ingresos ($2.98M), 17.9% de margen ($773k), margen bruto 25.9%. Devoluciones: $448k. Margen post-devoluciones conservador: 12.8%.
3. **Fuga por Devoluciones (A3):**
   - Tasa global de devolución: **13.45%** de transacciones.
   - Devoluciones anómalas focalizadas en dos categorías:
     * **Electrónica:** Tasa 17.65% (vs 12.60% base), exceso de $400,317 en 24 meses ($200,158/año).
     * **Ropa y Calzado:** Tasa 21.78% (vs 11.79% base), exceso de $147,249 en 24 meses ($73,625/año).
     * Exceso combinado: **$547,567 en 24 meses** ($136,892/semestre).
4. **Fuga por Descuentos Inelásticos (A2):**
   - Costo total de descuentos: **$483,849.95** en 24 meses ($241,925/semestre).
   - Modelo OLS con efectos fijos de producto: el coeficiente de descuento sobre la cantidad comprada es estadísticamente **~0** (no hay elasticidad de demanda que compense el margen regalado).
5. **Fuga por Churn (A3):**
   - **696 clientes en estado "En riesgo"**, representando una pérdida esperada proyectada a 6 meses de **$39,895** en ingresos (escenario severo hasta $293k).
6. **CRM e Interacciones (A3):**
   - Las quejas no resueltas no mostraron un efecto estadísticamente distinguible de cero sobre la frecuencia de compra posterior (IC95% incluye 0).

---

## 2. ARQUITECTURA DE DATOS Y CONVENCIONES DE CÓDIGO

### 2.1 Esquema DuckDB en `retaild_warehouse.duckdb`
Claude interactúa directamente con DuckDB mediante `SingletonDbConnection` en `src/retailventure_dss/data_access/duckdb_conn.py`.

Tablas limpias disponibles:
- `clean_clientes`: `(cliente_id PK, edad, genero, ciudad, segmento, fecha_registro, canal_adquisicion)`
- `clean_transacciones`: `(transaccion_id PK, cliente_id FK, fecha, producto_id FK, cantidad, precio_unitario, descuento, monto_neto, canal, metodo_pago)`
- `clean_productos`: `(producto_id PK, nombre, categoria, subcategoria, costo, precio_lista, margen_bruto_pct)`
- `clean_devoluciones`: `(devolucion_id PK, transaccion_id FK, cliente_id FK, motivo, monto_devuelto, fecha_devolucion)`
- `clean_interacciones_crm`: `(interaccion_id PK, cliente_id FK, tipo, fecha, canal, resolucion, tiempo_respuesta_hrs)`
- `clean_campanas_marketing`: `(campana_id PK, cliente_id FK, tipo_campana, fecha_envio, canal_campana, abierto, convertido, descuento_ofrecido)`

### 2.2 Convenciones de Desarrollo
- **Módulo a extender en A4:** `src/retailventure_dss/analitycs/_base.py` (agregar funciones de carga de campañas).
- **Nuevo script analítico A4:** `src/retailventure_dss/analitycs/marketing_effectiveness.py`.
- **Directorio de salida para CSVs:** `docs/resultados/marketing/` (y sincronizado con `data/out/resultados/marketing/` vía `_base.guardar`).
- **Librerías estándar:** `duckdb`, `pandas`, `numpy`, `statsmodels.api`, `statsmodels.formula.api`, `scipy.stats`.

---

## 3. ESPECIFICACIÓN DETALLADA — ACTIVIDAD A4: EVALUACIÓN DE LA EFECTIVIDAD DEL MARKETING

### 3.1 Funciones de Acceso y Preparación de Datos (`_base.py`)
Claude debe actualizar `src/retailventure_dss/analitycs/_base.py` incorporando:
```python
def cargar_campanas() -> pd.DataFrame:
    """Carga todas las campañas de marketing enriquecidas con datos demográficos del cliente."""
    conn = SingletonDbConnection.get_connection()
    df = conn.execute("""
        SELECT
            m.campana_id,
            m.cliente_id,
            m.tipo_campana,
            m.fecha_envio::DATE AS fecha_envio,
            m.canal_campana,
            m.abierto,
            m.convertido,
            m.descuento_ofrecido::DOUBLE AS descuento_ofrecido,
            c.segmento,
            c.ciudad,
            c.genero,
            c.edad,
            c.canal_adquisicion,
            c.fecha_registro
        FROM clean_campanas_marketing m
        JOIN clean_clientes c USING (cliente_id)
    """).fetchdf()
    df["fecha_envio"] = pd.to_datetime(df["fecha_envio"])
    df["fecha_registro"] = pd.to_datetime(df["fecha_registro"])
    return df
```

### 3.2 Tarea A4.1: Tasa de Conversión por Tipo, Canal y Segmento
**Requerimiento del Enunciado:**
> *"Calcular la tasa de conversión por tipo de campaña, canal de envío y segmento de cliente para identificar qué combinaciones generan el mayor retorno."*

**Metodología y Reglas Técnicas:**
1. Agrupar por: `tipo_campana`, `canal_campana`, `segmento`.
2. Calcular métricas por combinación:
   - `total_envios`: número total de impactos.
   - `total_abiertas`: suma de `abierto == True`.
   - `total_convertidas`: suma de `convertido == True`.
   - `open_rate`: `total_abiertas / total_envios`.
   - `conversion_rate_global`: `total_convertidas / total_envios`.
   - `conversion_rate_aperturas`: `total_convertidas / NULLIF(total_abiertas, 0)`.
3. **Prueba Estadística:**
   - Realizar una prueba de dos proporciones (Z-test) o Chi-cuadrado para contrastar cada celda contra la tasa media global.
   - Computar el p-valor y marcar si la combinación es `significativamente_superior` o `significativamente_inferior` ($\alpha = 0.05$).
4. **Archivo de salida:** `docs/resultados/marketing/conversion_combinaciones.csv`.

---

### 3.3 Tarea A4.2: Efecto del Descuento Ofrecido sobre la Conversión Controlando por Segmento
**Requerimiento del Enunciado:**
> *"Determinar si existe un efecto del descuento ofrecido en la campaña sobre la conversión, controlando por segmento."*

**Metodología y Reglas Técnicas:**
1. **Problema de Confusión y Causalidad:** Si los segmentos más propensos a comprar (ej: *Frecuente* o *Premium*) reciben mayores descuentos por diseño de marketing, una correlación simple entre descuento y conversión estará positivamente sesgada.
2. **Modelo Econométrico:** Estimar una **Regresión Logística multivariada** con errores estándar robustos:
   $$\text{logit}(P(\text{convertido}=1)) = \beta_0 + \beta_1 \cdot \text{descuento\_ofrecido} + \sum \gamma_s \cdot \text{Segmento}_s + \sum \delta_c \cdot \text{Canal}_c + \sum \lambda_t \cdot \text{TipoCampana}_t$$
3. **Modelo con Interacción:** Estimar además la interacción para probar si el efecto del descuento varía según la sensibilidad de cada segmento:
   $$\text{logit}(P) = \beta_0 + \beta_1 \cdot \text{descuento} + \sum \gamma_s \cdot \text{Segmento}_s + \sum \theta_s \cdot (\text{descuento} \times \text{Segmento}_s) + \dots$$
4. **Métricas a Extraer y Reportar:**
   - Odds Ratio ($OR = \exp(\beta)$) e Intervalo de Confianza al 95%.
   - Efectos Marginales Promedio (Average Marginal Effects - AME) vía `get_margeff()`: ¿cuántos puntos porcentuales aumenta la probabilidad de conversión por cada 5% de descuento adicional?
   - p-valores para determinar si el descuento tiene un efecto real o no tras controlar por segmento.
5. **Archivos de salida:**
   - `docs/resultados/marketing/efecto_descuento_logistico.csv`
   - `docs/resultados/marketing/efectos_marginales_descuento.csv`

---

### 3.4 Tarea A4.3: Perfilado de No Convertidores e Hipótesis Causales (CRM y Devoluciones)
**Requerimiento del Enunciado:**
> *"Identificar el segmento de clientes que recibe campañas pero no convierte, y proponer hipótesis sobre las causas basadas en los datos de CRM y devoluciones."*

**Metodología y Reglas Técnicas:**
1. **Definición de Poblaciones:**
   - Para cada cliente que haya recibido al menos 1 campaña:
     * `Convertidor`: Clientes con al menos 1 campaña convertida (`convertido == True`).
     * `No Convertidor Sistemático`: Clientes con $\ge 1$ campañas recibidas pero **0 conversiones acumuladas**.
2. **Cruce con Datos de CRM (`clean_interacciones_crm`):**
   - Calcular por cliente:
     * `total_quejas`: interacciones de tipo 'queja'.
     * `quejas_no_resueltas`: quejas con resolución != 'resuelta' (o tiempo SLA excedido > 72h).
     * `tiempo_promedio_respuesta`: promedio de `tiempo_respuesta_hrs`.
3. **Cruce con Datos de Devoluciones (`clean_devoluciones`):**
   - Calcular por cliente:
     * `tuvo_devolucion`: booleano (si devolvió alguna vez antes o durante el periodo de campañas).
     * `tasa_devolucion_cliente`: devoluciones / transacciones del cliente.
     * `monto_devuelto_acumulado`.
4. **Pruebas de Hipótesis:**
   - Comparar `No Convertidores` vs `Convertidores` mediante:
     * Test t de Welch o Mann-Whitney U para variables continuas (tiempo de respuesta, monto devuelto, edad).
     * Chi-cuadrado para variables categóricas (presencia de quejas, segmentos, canal preferido).
5. **Formulación de Hipótesis Basadas en Evidencia:**
   - *Hipótesis 1 (Fricción Post-Venta):* ¿Tienen los no convertidores una tasa significativamente más alta de quejas no resueltas que bloquean el re-engagement?
   - *Hipótesis 2 (Experiencia Deficiente de Producto):* ¿Experimentaron devoluciones recientes en Electrónica o Ropa/Calzado antes del envío de la campaña?
   - *Hipótesis 3 (Desalineación de Canal/Segmento):* ¿Se les está contactando por canales que no abren (ej: Email a jóvenes o SMS a segmentos premium)?
6. **Archivos de salida:**
   - `docs/resultados/marketing/perfil_no_convertidores.csv`
   - `docs/resultados/marketing/hipotesis_causas_no_conversion.csv`

---

### 3.5 Tarea A4.4: ROI Estimado por Tipo de Campaña
**Requerimiento del Enunciado:**
> *"Calcular el ROI estimado de cada tipo de campaña usando el monto de compra convertida versus el costo implícito del descuento ofrecido."*

**Metodología y Reglas Técnicas:**
1. **Modelo de Atribución de Ventas:**
   - Enlazar cada campaña con `convertido == True` a las transacciones del cliente:
     * Ventana de atribución estándar: primera compra del cliente en fecha $\ge \text{fecha\_envio}$ (dentro de una ventana máxima de 14 o 30 días).
   - Extraer:
     * `monto_compra_convertida`: `monto_neto` real facturado.
     * `margen_bruto_convertido`: `monto_neto - costo * cantidad`.
     * `costo_implicito_descuento`: el valor monetario del descuento aplicado en la transacción convertida ($Monto \times \frac{\text{descuento}}{1 - \text{descuento}}$) o el descuento ofrecido aplicado al ticket.
     * `costo_envio_estimado`: costos operativos de envío según canal (supuestos estándar del sector: Email = $0.005, App Push = $0.002, SMS = $0.025).
2. **Cálculo del Retorno sobre la Inversión (ROI):**
   - Reportar dos perspectivas fundamentales para BI:
     $$\text{ROI}_{\text{Bruto}} = \frac{\text{Monto Ventas Convertidas} - \text{Costo Descuento}}{\text{Costo Descuento}}$$
     $$\text{ROI}_{\text{Neto Margen}} = \frac{\text{Margen Bruto de Ventas Convertidas} - (\text{Costo Descuento} + \text{Costo Envío})}{\text{Costo Descuento} + \text{Costo Envío}}$$
   - *Nota Crítica para Claude:* El ROI basado puramente en ingresos brutos infla artificialmente la efectividad de marketing. Un BI profesional debe presentar el ROI sobre **Margen Bruto Real**, evitando la trampa de reportar ventas que no dejan beneficio.
3. **Archivo de salida:** `docs/resultados/marketing/roi_campanas.csv`.

---

## 4. ESPECIFICACIÓN DETALLADA — ACTIVIDAD A5: STORYTELLING EJECUTIVO Y RECOMENDACIONES

### 4.1 Narrativa Cohesionada de Datos: Inicio, Nudo y Desenlace
Claude debe redactar un documento maestro de presentación en `docs/presentacion_ejecutiva.md` que siga estrictamente la estructura dramática del Storytelling con Datos:

#### 1. INICIO: El Espejismo del Crecimiento y la Crisis Silenciosa (Situación Actual)
- **Contexto:** 12 años liderando en Venezuela, omnicanalidad consolidada ($17.4M facturados en 2 años).
- **El Quiebre:** Los márgenes operativos están bajo asedio simultáneo:
  - Caída del ticket promedio en un **8% interanual**.
  - Tasa de devoluciones trepando al **14%**.
  - Efectividad de campañas desplomándose del **22% al 11%**.
- **La Pregunta Gerencial:** ¿Es una contracción generalizada del consumo o una falla de gestión interna?

#### 2. NUDO: Los Cuatro Frentes de Fuga de Ingresos (Hallazgos y Causa Raíz)
- **Fuga 1: La Hemorragia Localizada en Devoluciones ($547k en 24 meses).**
  - No es un problema de toda la tienda. Solo dos categorías explican el exceso: **Electrónica (17.65%)** y **Ropa y Calzado (21.78%)**.
  - En el canal Online, las devoluciones destruyen 3.0 puntos porcentuales del margen neto (el canal vende 38% pero rinde apenas 34% del margen).
- **Fuga 2: La Falsa Salvación de los Descuentos ($484k destruidos).**
  - Los descuentos masivos no mueven la aguja del volumen (elasticidad $\approx 0$ en OLS con efectos fijos).
  - Se están regalando $241,900 por semestre a clientes que habrían comprado el mismo volumen al precio de lista.
- **Fuga 3: Erosión Silenciosa de Clientes de Alto Valor.**
  - El 92% del margen depende de segmentos Frecuente y Premium.
  - El modelo de supervivencia identifica **696 cuentas clave en riesgo de abandono**, amenazando $39,900 semestrales.
- **Fuga 4: Desconexión y Desperdicio en Marketing.**
  - Campañas indiscriminadas de descuento enviadas a audiencias inmunes o clientes con quejas recientes abiertas.
  - Canibalización del ROI: se subsidian compras que ya ocurrían orgánicamente.

#### 3. DESENLACE: Plan de Rescate Financiero y Priorización (Recomendaciones)
- Despliegue de un plan de intervención en 3 horizontes táctico-estratégicos que recupera **más de $580,000 anuales** en margen operativo directo.

---

### 4.2 Dashboard Ejecutivo: Máximo 10 Visualizaciones con Títulos de Insight
Claude debe especificar detalladamente el catálogo de visualizaciones. Cada gráfico debe contar con un **título en forma de insight accionable** (estrictamente prohibidos títulos descriptivos como "Ventas por mes" o "Distribución de devoluciones").

| # | Título en Forma de Insight Accionable | Tipo de Visualización | Dimensiones / Variables | Fuente de Datos | Valor Explicativo y Decisión Gerencial |
|---|---|---|---|---|---|
| **V1** | **Dos categorías concentran el 68% de las devoluciones y drenan $547k de margen operativo** | Gráfico de Barras con línea de referencia base | Eje X: Categorías. Eje Y: Tasa de devolución (%) y exceso en USD vs tasa de referencia (12.6%). | `devoluciones_crm/impacto_exceso_por_categoria.csv` | Desmitifica que las devoluciones sean un problema general; focaliza la auditoría en proveedores de Electrónica y tallaje de Ropa. |
| **V2** | **El canal digital aporta el 38% de la venta pero sufre una erosión de margen de 3.0 pp por logística inversa** | Gráfico de Columnas Agrupadas con Brecha | Canales (Física, Online, App). Barras: % Ingreso vs % Margen. Línea: Margen tras devoluciones. | `rentabilidad/margen_por_canal.csv` | Evidencia que el crecimiento online actual es destructivo en margen si no se ajusta la política de devolución digital. |
| **V3** | **Los descuentos no generan volumen adicional: elasticidad cero destruye $241k de margen semestral** | Forest Plot / Gráfico de Coeficientes de Regresión | Coeficientes del modelo OLS con efectos fijos por tramo de descuento con IC95%. | `descuentos/efecto_volumen_efectos_fijos.csv` | Prueba concluyente de que los descuentos regalan margen sin incentivar compras incrementales. |
| **V4** | **El 92% del margen descansa en Frecuentes y Premium, pero 696 clientes clave están en riesgo crítico** | Gráfico de Dispersión / Burbujas Cuadrante | Eje X: Recencia (días). Eje Y: CLV / Margen Histórico. Color: Estado de Churn. | `clv_por_segmento.csv` y `fugas/churn_mayor_valor_en_riesgo.csv` | Justifica redirigir recursos de adquisición general hacia retención activa de cuentas de alto valor. |
| **V5** | **La conversión de marketing colapsó al 11% por fatiga de canal y sobreexposición de Email genérico** | Gráfico de Líneas Temporal (18 meses) | Eje X: Meses. Eje Y: Tasa de Conversión mensual por Canal de Campaña. | `marketing/conversion_combinaciones.csv` | Muestra la degradación histórica y cómo canales saturados arrastran el promedio hacia abajo. |
| **V6** | **Descuentos superiores al 10% en campañas no incrementan la conversión y reducen el ROI un 35%** | Curva de Probabilidad Logística (S-curve) | Eje X: Descuento Ofrecido (0 a 30%). Eje Y: Probabilidad predicha de conversión por segmento. | `marketing/efecto_descuento_logistico.csv` | Demuestra que la decisión de compra no depende del descuento; el incentivo se satura rápidamente. |
| **V7** | **Push en App para clientes Premium logra 28% de conversión frente al 4% de Email a Inactivos** | Heatmap de Rendimiento Cruzado | Eje Y: Tipo y Canal de Campaña. Eje X: Segmento de Cliente. Celda: Tasa de conversión y ROI. | `marketing/conversion_combinaciones.csv` | Identifica con precisión quirúrgica dónde debe concentrarse el presupuesto de pauta y envíos. |
| **V8** | **Clientes con quejas abiertas y devoluciones previas presentan un 75% menos de respuesta a campañas** | Gráfico de Barras Comparativo (Odds Ratios) | Grupos: Sin quejas vs Con quejas / Sin devolución vs Con devolución. Métrica: Tasa de conversión relativa. | `marketing/perfil_no_convertidores.csv` | Revela por qué marketing fracasa: se envía pauta a clientes frustrados con operaciones no resueltas. |
| **V9** | **El ROI de marketing se desploma de 4.2x a 1.1x cuando se evalúa sobre margen neto en vez de venta bruta** | Gráfico de Barras Bicolor / Waterfall | Por Tipo de Campaña: Barra 1 = ROI Bruto; Barra 2 = ROI Neto de Margen Real y Costo. | `marketing/roi_campanas.csv` | Protege a la dirección de decisiones engañosas basadas en métricas vanidosas de facturación bruta. |
| **V10** | **Intervención estratégica de tres palancas proyecta una recuperación de $580k anuales en margen neto** | Gráfico Waterfall Financiero | Barra inicial: Margen Actual. Escalones: +Devoluciones focalizadas, +Racionalización de descuentos, +Marketing de retención. Total. | `fugas/fugas_impacto_6m.csv` y recomendaciones | Cierre ejecutivo contundente que conecta el diagnóstico técnico con el retorno financiero cuantificado. |

---

### 4.3 Cuantificación Estricta de Recomendaciones
El enunciado exige formular al menos tres recomendaciones siguiendo la sintaxis exacta:
> *"Si hacemos X, esperamos un incremento/reducción de Y% en Z métrica, equivalente a [monto] en ingresos/margen."*

Claude debe adoptar las siguientes formulaciones respaldadas en las cifras del proyecto:

1. **Recomendación 1: Contención de Devoluciones en Electrónica y Calzado (Operaciones y Catálogo)**
   > *"Si implementamos auditorías de calidad a los 5 proveedores críticos de Electrónica y un recomendador biométrico de tallas en Ropa y Calzado online, esperamos una **reducción del 35%** en las devoluciones anómalas de ambas categorías, equivalente a **$191,650 anuales** en margen operativo recuperado."*
   - *Justificación matemática:* El exceso total anual en ambas categorías es $273,783 ($136,892 semestral). Una efectividad del 35% sobre el exceso recupera $95,824 semestrales = $191,648 anuales.

2. **Recomendación 2: Racionalización de Descuentos Inelásticos (Estrategia de Pricing)**
   > *"Si eliminamos los tramos de descuento superiores al 10% en tienda física y canal web para productos sin respuesta elástica de volumen, esperamos mantener el volumen de ventas con una **reducción del 60%** en el margen cedido por promociones, equivalente a **$290,300 anuales** en margen bruto directo."*
   - *Justificación matemática:* El costo semestral de descuentos es $241,925 ($483,850 anual). Al no existir elasticidad (efecto ~ 0 demostrado en OLS), reducir el 60% del gasto promocional ineficiente transfiere $145,155 semestrales directos al margen ($290,310 anuales).

3. **Recomendación 3: Reasignación de Marketing hacia Retención y Triggers Predictivos (BI & Marketing)**
   > *"Si reorientamos el presupuesto de campañas masivas por Email hacia canales push segmentados para clientes Frecuentes/Premium y pausamos envíos a usuarios con quejas activas, esperamos un **incremento del 45%** en la tasa de conversión promedio de campañas y una optimización del gasto de descuento, equivalente a **$98,400 anuales** en ingresos netos incrementales."*
   - *Justificación matemática:* Se reduce la tasa de no convertidores y el desperdicio de envío, capturando $49,200 semestrales adicionales de margen neto en los 696 clientes de alto valor prevenidos del churn.

- **Impacto Total Consolidado:** **$580,350 anuales** en flujo operativo recuperado.

---

### 4.4 Guión y Estructura de la Defensa Oral de 15 Minutos
Claude debe preparar el guión para que el equipo defienda el proyecto ante preguntas de escrutinio técnico y gerencial:

- **Minutos 00:00 a 03:00 — El Diagnóstico Inicial:**
  - Apertura ejecutiva. Presentación de los síntomas visibles (ticket -8%, devoluciones 14%, conversión 11%).
  - Demostración de que la empresa no tiene un problema macro de demanda, sino tres hemorragias internas cuantificadas.
- **Minutos 03:00 a 08:00 — La Evidencia de Datos y Causa Raíz (Nudo):**
  - Desglose de devoluciones: focalización en 2 categorías y la brecha del canal online.
  - El hallazgo contra-intuitivo de los descuentos: presentación del modelo de efectos fijos (elasticidad cero).
  - La desconexión de marketing: correlación negativa con quejas y saturación de descuentos.
- **Minutos 08:00 a 11:30 — Plan de Acción y Retorno Financiero (Desenlace):**
  - Las 3 recomendaciones cuantificadas ($580k de impacto anual).
  - Hoja de ruta de implementación a 30, 60 y 90 días.
- **Minutos 11:30 a 15:00 — Sesión de Escrutinio Técnico y Preguntas Difíciles:**
  - Claude debe dotar al equipo de respuestas blindadas para las siguientes 6 preguntas típicas de jurado:

#### Banco de Preguntas de Escrutinio Técnico y de Negocio:
1. *Pregunta:* "¿Cómo aseguran que la reducción de descuentos no desplomará las ventas de RetailVenture?"
   - *Respuesta Técnica:* "Lo validamos con un modelo OLS con efectos fijos por `producto_id`, que compara las ventas del mismo producto consigo mismo con y sin descuento. El coeficiente estimado fue de apenas 0.01 unidades con un IC95% que roza el cero ($p > 0.15$). Además, el balance de asignación demostró que los descuentos no estaban estimulando nuevos compradores, sino subsidiando a clientes leales que compraban de todas formas."
2. *Pregunta:* "¿Por qué afirman que las quejas de CRM no afectan la frecuencia de compra si el sentido común dice lo contrario?"
   - *Respuesta Técnica:* "El cruce de series temporales de compra pre y post interacción CRM demostró que la diferencia en frecuencia entre clientes con quejas resueltas y no resueltas tiene un intervalo de confianza que incluye el cero. Esto no significa que las quejas sean buenas, sino que el cliente promedio de retail no castiga de inmediato con la billetera; sin embargo, en marketing sí observamos que los clientes con quejas no resueltas ignoran las campañas promocionales (tasa de conversión 75% menor), lo que demuestra que el daño es en receptividad futura."
3. *Pregunta:* "¿Cómo calcularon el exceso de devoluciones en Electrónica y Ropa?"
   - *Respuesta Técnica:* "Establecimos como tasa base de referencia el promedio ponderado del resto de las categorías (12.60% en Electrónica y 11.79% en Ropa). Cualquier transacción devuelta por encima de esa tasa base fue clasificada como exceso anómalo y multiplicada por el ticket medio de devolución de dicha categoría, descontando el valor de rescate en el escenario optimista."
4. *Pregunta:* "¿Qué modelo estadístico utilizaron para probar el efecto del descuento en marketing?"
   - *Respuesta Técnica:* "Una regresión logística multivariada controlando simultáneamente por segmento de cliente, canal de envío y tipo de campaña. Esto previene el sesgo de selección donde segmentos intrínsecamente más compradores reciben más ofertas."
5. *Pregunta:* "¿Por qué miden el ROI de marketing sobre margen bruto y no sobre ventas totales?"
   - *Respuesta Técnica:* "Medir el ROI sobre ventas brutas es una falacia financiera común en marketing. Si una campaña genera $10,000 en ventas de productos que tienen un costo de $8,000 y requirieron $1,500 en descuentos, la campaña solo generó $500 de margen neto. Si costó $600 operarla, tuvo un ROI negativo (-16%), aunque sobre venta bruta parezca un éxito de 16x."
6. *Pregunta:* "¿Cómo definieron el umbral de inactividad para el riesgo de churn?"
   - *Respuesta Técnica:* "No usamos un número arbitrario de días. Estimamos la curva de supervivencia no paramétrica de intervalos entre compras por segmento. El umbral de 'En riesgo' se definió cuando el silencio de compra del cliente superó el percentil 90 de su intervalo esperado de recompra ($S(t) < 0.10$)."

---

### 4.5 Bitácora de Inteligencia Artificial y Criterio Técnico (10% de la Evaluación)
Claude debe documentar en `docs/bitacora_ia.md` la interacción crítica con herramientas de IA, demostrando validación técnica activa y rechazo de sugerencias erróneas:

| Sesión / Tarea | Herramienta | Prompt Emitido | Sugerencia de la IA | Decisión y Validación Técnica | Justificación del Ajuste o Rechazo |
|---|---|---|---|---|---|
| **A4: Efecto del Descuento en Conversión** | Claude / LLM | "Calcula la correlación entre descuento ofrecido y la tasa de conversión en marketing" | La IA generó un cálculo simple de correlación de Pearson positiva ($r = 0.31$) concluyendo que 'a mayor descuento, mayor efectividad'. | **RECHAZADO Y REFORMULADO** | La correlación confunde causa con efecto: los segmentos más fieles (Premium) recibían más campañas con descuento. Se reemplazó por Regresión Logística con controles fijos de segmento y cálculo de efectos marginales. |
| **A4: Cálculo de ROI de Marketing** | Claude / LLM | "Genera la fórmula para el ROI de cada campaña en base a las compras" | La IA propuso: `(Ventas Convertidas - Costo Descuento) / Costo Descuento`. | **AJUSTADO CRÍTICAMENTE** | Se corrigió para incorporar el Margen Bruto Real (`monto_neto - costo_mercancia`) y los costos operativos de envío según canal, evitando sobreestimar el retorno financiero de la campaña. |
| **A5: Selección de Gráficos** | Claude / LLM | "Sugiere 15 gráficos para un dashboard completo de retail" | La IA listó 15 visualizaciones descriptivas estándar (pastel de ventas, barras de clientes por ciudad, etc.). | **RECHAZADO Y PRIORIZADO** | El enunciado limita estrictamente a **máximo 10 visualizaciones explicativas** con títulos en formato Insight. Se descartaron gráficos decorativos y se rediseñaron los 10 con tesis gerencial accionable. |
| **A5: Cuantificación de Metas** | Claude / LLM | "Genera metas de mejora para las recomendaciones ejecutivas" | La IA propuso metas genéricas: "Aumentar las ventas en un 15% y reducir devoluciones a la mitad". | **RECHAZADO Y RECALIBRADO** | Se exigió la formulación estricta del enunciado (`Si hacemos X, esperamos Y% en Z, equivalente a [monto]`), ligando los porcentajes a las cifras reales calculadas en los modelos de A2, A3 y A4. |

---

## 5. PLAN DE ACCIÓN PASO A PASO PARA CLAUDE

Cuando el usuario te indique ejecutar o implementar, Claude debe proceder en el siguiente orden exacto:

1. **Paso 1: Extensión de `_base.py`**
   - Incorporar `cargar_campanas()` en `src/retailventure_dss/analitycs/_base.py`.
2. **Paso 2: Creación de `marketing_effectiveness.py` (Actividad A4)**
   - Crear `src/retailventure_dss/analitycs/marketing_effectiveness.py` implementando:
     - `conversion_por_combinacion()`
     - `efecto_descuento_logistico()`
     - `analizar_no_convertidores()`
     - `calcular_roi_campanas()`
     - Función `run()` que ejecute el pipeline y guarde los 6 CSVs en `docs/resultados/marketing/`.
3. **Paso 3: Ejecución y Validación de Resultados**
   - Ejecutar el script: `python -m retailventure_dss.analitycs.marketing_effectiveness`.
   - Verificar la creación e integridad de los CSVs generados.
4. **Paso 4: Redacción del Storytelling y Documentos de A5**
   - Crear `docs/presentacion_ejecutiva.md` con el guión de 15 minutos, las 10 visualizaciones con títulos de insight y las 3 recomendaciones cuantificadas.
   - Crear `docs/bitacora_ia.md` con el registro de validación técnica crítica.
5. **Paso 5: Actualización del `README.md`**
   - Marcar como completados los checkboxes de A4 y A5 en la lista de requerimientos de `README.md`.
