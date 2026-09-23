# Proyecto 1: Sistema Inteligente Adaptativo con Datos No Estacionarios

**Curso:** Planificación y Toma de Decisiones en IA, UTEC (2026-2)  
**Profesores:** Dra. Aurea Soriano-Vargas & Mg. Robert Buleje  
**Caso de Uso Elegido:** Detección de Fraude Financiero en E-Commerce (IEEE-CIS Fraud Detection)  
**Modalidad de Presentación:** Documento / PPT (10 - 15 minutos)  
**Puntaje del Avance en Rúbrica:** 2 Puntos (de 20)

---

## 1. Contextualización y Planteamiento del Problema

En el sector de comercio electrónico (e-commerce), el fraude transaccional representa una de las mayores amenazas operativas y financieras. Según estimaciones de la Federal Trade Commission (FTC) y reportes especializados del sector (como Merchant Savvy y Statista), las pérdidas por fraude en e-commerce superan los **$48 mil millones de dólares anuales a nivel global**, con un impacto superior a los **$10 mil millones en EE.UU.** Este impacto comprende tanto pérdidas directas de capital como costos operativos significativos por la investigación manual y el bloqueo erróneo de transacciones legítimas de usuarios reales.

Asimismo, los patrones de compra y las tácticas fraudulentas presentan un continuo **cambio en el comportamiento de los datos** a lo largo del tiempo, impulsado por nuevas tecnologías de pago, estacionalidades comerciales y la rápida adaptación de los atacantes. Los modelos predictivos estáticos pierden efectividad a medida que transcurre el tiempo al no ajustarse a este dinamismo. Por todos estos motivos, **se propone implementar un sistema inteligente adaptativo de detección de fraude en e-commerce, capaz de evaluar su desempeño a lo largo del tiempo y preservar su robustez operacional mediante estrategias de adaptación temporal.**

### Justificación del Dataset
Se elige **IEEE-CIS Fraud Detection** porque combina una evolución gradual de los hábitos de consumo con cambios más bruscos por nuevas campañas de fraude, y porque su alta cantidad de variables y el fuerte desbalance de clases (~3.5% de transacciones fraudulentas) lo hacen representativo de un problema real de este tipo.

---

## 2. Definición de Objetivos

### Objetivo General
Implementar un sistema inteligente de detección de fraude transaccional para el sector e-commerce, capaz de evaluar su desempeño en el tiempo y adaptarse al cambio en el comportamiento de los datos para preservar la robustez del servicio a lo largo de su ciclo de vida.

### Objetivos Específicos (Secuenciales)
1. **Exploración Temporal:** Analizar la dimensión temporal del conjunto de datos transaccionales para identificar patrones de distribución, anomalías y variaciones no estacionarias a lo largo del tiempo.
2. **Modelado Comparativo:** Comparar el desempeño de dos modelos clásicos y modelos avanzados en la detección de fraude bajo un esquema de evaluación cronológico.
3. **Arquitectura del Sistema:** Diseñar la arquitectura del sistema a nivel de componentes.
4. **Evaluación de Escenarios:** Analizar el comportamiento temporal del sistema bajo diferentes escenarios de políticas de olvido basadas en ventanas deslizantes para evaluar su capacidad de adaptación y robustez.

---

## 3. Definición de Restricciones (Operativas de Negocio)

1. **Latencia Operacional:** El tiempo máximo de inferencia debe ser menor a **200 ms por transacción** para garantizar que el flujo de aprobación en la pasarela de pagos opere sin interrupciones perceptibles para el comprador. Respaldado en literatura: Borketey (2024) sobre tiempos de respuesta en detección de fraude en tiempo real, y estándares industriales de latencia para APIs críticas.
2. **Disponibilidad de Información Mínima:** El sistema opera únicamente con el conjunto de atributos que habitualmente proveen las pasarelas de pago estándar, sin garantía de fuentes adicionales de verificación de identidad ni de registros siempre completos.
3. **Consistencia Temporal Estricta:** Al incorporar nueva información, esta no debe mezclarse con datos de periodos posteriores ya conocidos: cada decisión y cada actualización del modelo solo puede usar información disponible hasta ese momento.

---

## 4. Diseño del Sistema de IA (Arquitectura de Componentes)

El sistema se diseña como un pipeline de 5 componentes explícitos, con un monitor de drift y un ciclo de retroalimentación que cierran el circuito de adaptación continua:

```
[Fuentes de Datos]  →  ①Adquisición   →  ②Módulo       →  ③Manejo de      →  ④Módulo de    →  ⑤Componente
                        e Integración      Predictivo         Incertidumbre       Decisión          de Acción
                        (Feature Store)    (4 modelos         (calibración de     (umbral           → Aprobar
                                            candidatos)        score / confianza)  costo-óptimo)     → Marcar para
        ↑                                          ↑                                                   revisión
        │                                [Monitor de Drift]                                          (analista)
        └───────── feedback: etiquetas ── (ventanas deslizantes,                                        │
                    reales para reentrenar   dispara reentrenamiento) ◄──────────────────────────────────┘
```

1. **Adquisición e integración de datos:** unifica las fuentes disponibles (variables transaccionales, categóricas de dispositivo/email y señales de comportamiento del comprador) en una capa de features consistente en el tiempo.
2. **Módulo predictivo:** los 4 modelos candidatos (sección 6) generan un score de probabilidad de fraude por transacción.
3. **Manejo de incertidumbre:** las predicciones de alta confianza se resuelven automáticamente y las de score ambiguo se marcan para revisión.
4. **Módulo de toma de decisiones:** aplica el umbral costo-óptimo (ver métricas de decisión, sección 6) sobre el score para decidir la acción a ejecutar.
5. **Componente de acción:** ejecuta la respuesta final, que es aprobar la transacción o derivarla a un analista de fraude para revisión.

El **monitor de drift** (ventanas deslizantes sobre el F1-Score, sección 8) dispara el reentrenamiento del módulo predictivo, y las etiquetas reales resultantes de la acción (fraude confirmado o no) retroalimentan la capa de adquisición de datos, cerrando el ciclo de adaptación continua.

---

## 5. Métricas de Éxito

### A. Métrica Técnica
* **F1-Score y ROC-AUC:** Evaluadas por bloques temporales para cuantificar la capacidad de discriminación bajo clases altamente desproporcionadas.
  $$\text{F1} = 2 \times \frac{\text{Precision} \times \text{Recall}}{\text{Precision} + \text{Recall}}$$
* **Latencia Promedio:** Tiempo de respuesta inferior a 200 ms por predicción.

### B. Métrica de Decisión (Negocio)
* **Costo Neto por Error:** Balance económico entre el costo del fraude omitido (Falso Negativo) y el costo operativo/fricción por revisión manual de compras legítimas (Falso Positivo):
  $$\text{Costo Total} = (\text{FN} \times \text{Monto Promedio del Fraude}) + (\text{FP} \times \text{Costo de Fricción})$$
* **Estimado Cuantitativo de Negocio:**
  * En una pasarela que procesa 10,000 transacciones mensuales con una tasa de fraude del 3.5% (350 fraudes):
  * Asumiendo un costo de \$15 por revisión/fricción de un Falso Positivo y una pérdida promedio de \$120 por cada Falso Negativo no detectado:
  * Si un modelo no adaptado permite que los FN aumenten en 40 casos por mes, la pérdida económica directa asciende a \$4,800 mensuales solo por fraude omitido. Optimizar la adaptación y umbrales reduce simultáneamente la fricción y el capital perdido, generando ahorros proyectados de miles de dólares por ciclo de facturación.

### C. Métrica Social / Riesgo
* **Equidad en la Tasa de Falsos Positivos por Rango de Monto:** Garantizar que los usuarios con compras legítimas de bajo ticket no sufran tasas de bloqueo artificialmente elevadas respecto a transacciones corporativas o de montos elevados.

---

## 6. Modelos Mapeados

Para este proyecto se evaluarán 4 modelos complementarios organizados en dos categorías:

* **Modelos Clásicos (Línea Base):**
  * **Regresión Logística:** Modelo lineal interpretable de referencia inicial, de bajo costo computacional y evaluación directa.
  * **Random Forest Classifier:** Ensamble por bagging que captura relaciones no lineales entre variables transaccionales.
* **Modelos Avanzados:**
  * **LightGBM:** Ensamble por Gradient Boosting de alta velocidad, optimizado para grandes volúmenes tabulares con partición por hojas (leaf-wise).
  * **XGBoost:** Algoritmo de boosting con regularización robusta, alta precisión predictiva y soporte nativo para valores faltantes.

---

## 7. Monitoreo y Políticas de Olvido (Respaldos Teóricos y Escenarios)

Siguiendo las indicaciones de la cátedra y literatura especializada (*Gama et al., 2014; Dal Pozzolo et al., 2018*):
* **Regla de Activación (Política):** Se evalúa el F1-Score en bloques temporales. Si se registra una degradación superior al **5%** respecto a la ventana base, se dispara la alerta de reentrenamiento.
* **Exploración por Escenarios de Olvido:**
  * **Escenario A (Olvido Abrupto):** Reentrenamiento estricto sobre ventanas recientes de amplitud variable para estudiar la velocidad de ajuste del modelo ante cambios de patrón.
  * **Escenario B (Olvido Ponderado):** Asignación de pesos decrecientes en el tiempo (*time-decay weighting*) para retener conocimiento estructural histórico pero priorizando las transacciones recientes.
  * **Análisis de Sensibilidad de Ventanas:** Contrastar múltiples tamaños de ventana para identificar experimentalmente el balance óptimo entre estabilidad del clasificador y costo computacional de reentrenamiento.

---

## 8. Mini Plan de Trabajo

* **Fase 1 (Actual):** Formulación del problema, objetivos pulidos, restricciones operativas, diseño de la arquitectura del sistema, métricas con fórmulas y dataset IEEE-CIS (Completado - Avance 2 Pts).
* **Fase 2 (Próxima):** Exploración temporal (EDA), ingeniería de variables temporales agregadas y partición cronológica estricta.
* **Fase 3 (Desarrollo):** Entrenamiento comparativo de los 4 modelos (LogReg, Random Forest, LightGBM, XGBoost).
* **Fase 4 (Entrega Final):** Simulación de escenarios de políticas de olvido, análisis de degradación e informe técnico final (máximo 8 páginas).
