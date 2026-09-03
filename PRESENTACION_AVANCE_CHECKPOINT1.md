# Avance Proyecto 1: Sistema Inteligente Adaptativo con Datos No Estacionarios

**Curso:** Planificación y Toma de Decisiones en IA — UTEC (2026-2)  
**Profesores:** Dra. Aurea Soriano-Vargas & Mg. Robert Buleje  
**Caso de Uso Elegido:** Detección de Fraude Financiero en E-Commerce (IEEE-CIS Fraud Detection)  
**Modalidad de Presentación:** Documento / PPT (10 - 15 minutos)  
**Puntaje del Avance en Rúbrica:** 2 Puntos (de 20)

---

## 1. Contextualización y Planteamiento del Problema

En el sector de comercio electrónico (e-commerce), las transacciones digitales han experimentado un crecimiento acelerado, lo que ha incrementado los ataques de fraude financiero. El fraude representa pérdidas monetarias directas para los comercios, así como costos por fricción y pérdida de clientes legítimos debido a falsos bloqueos (falsos positivos).

Dado que los patrones de fraude evolucionan constantemente a lo largo del tiempo por la aparición de nuevas tácticas delictivas (Concept Drift), los modelos estáticos pierden efectividad rápidamente al no considerar el cambio en la distribución de los datos. Por estos motivos, se propone el presente proyecto para desarrollar e implementar un sistema inteligente adaptativo de detección de fraude en e-commerce, capaz de evaluar su degradación y mantener su rendimiento operacional a lo largo del tiempo mediante estrategias de adaptación temporal.

---

## 2. Definición de Objetivos

### Objetivo General
Implementar un sistema inteligente de detección de fraude transaccional para el sector e-commerce, capaz de evaluar el rendimiento en el tiempo y adaptarse a la variación no estacionaria de los datos (Concept Drift) para mantener la robustez del servicio a lo largo de su ciclo de vida.

### Objetivos Específicos (Secuenciales)
1. **Analizar y explorar la dimensión temporal** del conjunto de datos transaccionales para identificar patrones de distribución, anomalías y variaciones no estacionarias a lo largo del tiempo.
2. **Implementar y comparar modelos de clasificación supervisada** (evaluando dos enfoques tradicionales y uno avanzado) en estricto orden cronológico para establecer la línea base de rendimiento.
3. **Diseñar la arquitectura del sistema a nivel de componentes**, definiendo la integración de datos, el módulo predictivo, el módulo de toma de decisiones, el manejo de incertidumbre y el componente de acción.
4. **Analizar escenarios de simulación temporal** mediante políticas de olvido con ventanas deslizantes de diferente tamaño (30, 60 y 90 días) para evaluar la robustez y degradación del sistema ante variaciones en la distribución de los datos.

---

## 3. Definición de Restricciones (Operativas de Negocio)

1. **Latencia Operacional:** El tiempo máximo de predicción e inferencia debe ser menor a 200 ms por transacción para garantizar que el proceso de pago no sufra interrupciones en la pasarela.
2. **Estandarización de Fuentes de Datos:** El sistema debe procesar e integrar entradas heterogéneas provenientes de múltiples puntos de venta y dispositivos bajo un esquema estandarizado unificado.
3. **Evaluación Cronológica Estricta:** Las pruebas del sistema prohíben el uso de validación cruzada aleatoria (k-fold) para evitar la contaminación de información del futuro hacia el pasado (data leakage).

---

## 4. Métricas de Éxito Compactas

* **Métrica Técnica:** F1-Score y ROC-AUC evaluados por bloque temporal para medir la capacidad discriminativa bajo desbalance de clases.
* **Métrica de Decisión (Negocio):** Costo Neto por Error, equilibrando el costo del fraude omitido (Falso Negativo) frente al costo de fricción por revisión manual (Falso Positivo):
  $$\text{Costo Total} = (\text{Falsos Negativos} \times \text{Monto del Fraude}) + (\text{Falsos Positivos} \times \text{Costo de Fricción})$$
* **Métrica Social / Riesgo:** Equidad de Tasa de Falsos Positivos por Rango de Monto, asegurando que las transacciones legítimas de menor valor no sean rechazadas arbitrariamente.

---

## 5. Modelos Mapeados

* **Modelos Tradicionales (Línea Base):**
  * **Regresión Logística:** Modelo lineal interprete para establecer la referencia inicial.
  * **Random Forest Classifier:** Modelo de ensamble por bagging para capturar no linealidades.
* **Modelo Avanzado:**
  * **LightGBM / XGBoost:** Modelos basados en Gradient Boosting, optimizados para datos tabulares masivos, con manejo nativo de nulos y alta velocidad de entrenamiento.

---

## 6. Estrategia de Monitoreo: Evaluación por Escenarios de Olvido

Siguiendo las indicaciones prioritarias del profesor Mg. Robert Buleje:
* **Regla de Activación (Política):** Se monitorea el F1-Score en bloques fijos de tiempo. Si se detecta una caída mayor al 5% respecto al bloque base o baja de un umbral crítico, se activa la alerta de reentrenamiento.
* **Evaluación de Escenarios de Ventana:**
  * **Escenario A (Ventana corta - 30 días):** Reentrenar utilizando únicamente los últimos 30 días (olvido rápido de datos antiguos).
  * **Escenario B (Ventana mediana - 60 días):** Reentrenar con los últimos 60 días (balance entre estabilidad y frescura).
  * **Escenario C (Ventana Ponderada por Recencia):** Reentrenar asignando mayor peso probabilístico (time-decay) a los datos más recientes.

---

## 7. Mini Plan de Trabajo

* **Fase 1 (Actual):** Formulación del problema, objetivos reestructurados, restricciones de negocio, métricas y dataset IEEE-CIS (Completado - Avance 2 Pts).
* **Fase 2 (Próxima):** Exploración temporal (EDA) e ingeniería de características con ventanas deslizantes.
* **Fase 3 (Desarrollo):** Entrenamiento comparativo de modelos tradicionales vs. avanzado.
* **Fase 4 (Entrega Final):** Código del sistema, evaluación de escenarios de olvido e informe técnico de máximo 8 páginas.
