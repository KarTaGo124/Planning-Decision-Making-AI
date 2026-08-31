# Avance Proyecto 1: Sistema Inteligente Adaptativo con Datos No Estacionarios

**Curso:** Planificación y Toma de Decisiones en IA — UTEC (2026-2)  
**Profesores:** Dra. Aurea Soriano-Vargas & Mg. Robert Buleje  
**Caso de Uso Elegido:** Detección de Fraude Financiero en E-Commerce (IEEE-CIS Fraud Detection)  
**Modalidad de Presentación:** Documento / PPT (10 - 15 minutos)  
**Puntaje del Avance en Rúbrica:** 2 Puntos (de 20)

---

## 1. Definición de Objetivos

### Objetivo del Sistema
Desarrollar un sistema de clasificación supervisada capaz de detectar transacciones fraudulentas en tiempo real en una plataforma de e-commerce, considerando explícitamente la naturaleza dinámica y cambiante de las tácticas de fraude a lo largo del tiempo (Concept Drift).

### Objetivos Específicos
1. **Predicción Supervisada:** Clasificar las transacciones entrantes como legítimas (0) o fraudulentas (1).
2. **Respetar la Dimensión Temporal:** Realizar todo el proceso de entrenamiento, validación y prueba en estricto orden cronológico utilizando la marca de tiempo `TransactionDT`.
3. **Monitoreo Continuo:** Evaluar la degradación del rendimiento del modelo a medida que transcurren los bloques de tiempo mediante estrategias basadas en el olvido.

---

## 2. Definición de Restricciones

* **Operacionales (Latencia):** El tiempo de decisión por transacción debe ser menor a 200 ms para integrarse sin fricción en la pasarela de pagos.
* **Desbalance de Clases:** El conjunto de datos presenta un desbalance severo (aprox. 3.5% de fraudes frente al 96.5% de transacciones legítimas).
* **Calidad de Datos / Nulos:** Alta proporción de valores faltantes en atributos categóricos de identidad y dispositivos.
* **Validación Temporal Estricta:** No se utilizará validación cruzada aleatoria (k-fold) para evitar la fuga de información del futuro hacia el pasado (data leakage).

---

## 3. Métricas de Éxito

El desempeño del proyecto se medirá integrando las tres dimensiones requeridas:

### A. Métricas Técnicas
* **F1-Score:** Métrica principal dada la desproporción de clases.
* **ROC-AUC y PR-AUC:** Medición de la capacidad discriminativa del modelo en distintos umbrales de probabilidad.
* **Latencia:** Tiempo promedio por predicción en milisegundos.

### B. Métricas de Decisión (Costo / Negocio)
* **Costo Neto por Error:** Balance económico calculado como:
  $$\text{Costo Total} = (\text{Falsos Negativos} \times \text{Monto del Fraude}) + (\text{Falsos Positivos} \times \text{Costo de Fricción / Revisión})$$
* **Tasa de Cobertura de Fraude:** Porcentaje de volumen monetario riesgoso interceptado.

### C. Métricas Sociales y de Riesgo
* **Equidad por Rango de Monto:** Garantizar que la tasa de falsos positivos no afecte desproporcionadamente a transacciones de bajos montos.
* **Seguridad por Dispositivo:** Evaluar que el sistema no presente sesgos de rechazo arbitrario según el sistema operativo o navegador.

---

## 4. Modelos Mapeados

Para este proyecto se evaluarán las siguientes alternativas:

* **Modelos Tradicionales (Línea Base):**
  * **Regresión Logística:** Modelo lineal interprete para establecer la baseline inicial.
  * **Random Forest Classifier:** Modelo de ensamble por bagging para capturar no linealidades.
* **Modelo Avanzado:**
  * **LightGBM / XGBoost:** Modelos basados en Gradient Boosting, optimizados para datos tabulares masivos, con manejo nativo de nulos y alta velocidad.

---

## 5. Estrategia de Monitoreo: Ventanas Deslizantes Fijas

Siguiendo las indicaciones prioritarias del sílabo actualizado (Sección 3.5):
* **Estrategia Basada en el Olvido (Prioridad):** Se priorizará el uso de ventanas fijas deslizantes (ejemplo: bloques de 30 días con desplazamiento temporal).
* **Evaluación de Escenarios:** Se evaluará el impacto del drift variando la amplitud de la ventana deslizante para comparar la estabilidad frente a la adaptabilidad del modelo.
* **Gatillo de Adaptación:** Al detectar una caída del desempeño superior al umbral fijado (ejemplo: caída mayor al 5% en F1-Score), se activará una alerta de reentrenamiento periódico con la ventana más reciente.

---

## 6. Mini Plan de Trabajo y Entregables Finales

* **Fase 1 (Actual):** Formulación del problema, dataset, métricas y diseño conceptual (Completado - Avance 2 Pts).
* **Fase 2 (Próxima):** Exploración temporal (EDA) e ingeniería de características con ventanas deslizantes.
* **Fase 3 (Desarrollo):** Entrenamiento comparativo de modelos tradicionales vs. avanzado.
* **Fase 4 (Entrega Final):** 
  * Código del sistema funcional y reproducible.
  * Documento Técnico: **Informe de un máximo de 8 páginas**.
  * Elementos visuales e infografía final.
  * Presentación final en clase (15-20 minutos de exposición + 5-10 minutos de preguntas).
