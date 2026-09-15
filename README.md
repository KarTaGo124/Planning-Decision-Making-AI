# Planificación y Toma de Decisiones en IA, UTEC (2026-2)

Este repositorio contiene la propuesta y avances para los proyectos de la asignatura **Planificación y Toma de Decisiones en IA** en la Universidad de Ingeniería y Tecnología (UTEC), dictada por la **Dra. Aurea Soriano-Vargas** y el **Mg. Robert Buleje**.

---

## Proyecto 1: Sistema Inteligente Adaptativo con Datos No Estacionarios

Se presenta la formulación contextualizada del problema, la selección del conjunto de datos, los objetivos y restricciones del sistema, el diseño de su arquitectura y la estrategia de monitoreo temporal por escenarios para la **detección de fraude financiero en e-commerce**.

### Documentación:
* **Presentación Interactiva:** [`docs/PRESENTACION_PROYECTO1.html`](docs/PRESENTACION_PROYECTO1.html)
* **Documento Técnico de Apoyo:** [`docs/PRESENTACION_PROYECTO1.md`](docs/PRESENTACION_PROYECTO1.md)
* **Indicaciones del Proyecto:** [`docs/UTEC_2026_1__Planificación_y_Toma_de_Decisiones_en_IA.pdf`](<docs/UTEC_2026_1__Planificación_y_Toma_de_Decisiones_en_IA.pdf>)
* **Dataset Seleccionado:** IEEE-CIS Fraud Detection (Kaggle)
* **Puntos Clave Desarrollados:**
  1. Contextualización del Problema en E-Commerce respaldada con datos cuantitativos de la industria.
  2. Definición de Objetivos (General de Implementación + 4 Específicos Secuenciales).
  3. Definición de Restricciones Operativas de Negocio (Latencia < 200 ms, Información mínima garantizada y Consistencia temporal estricta).
  4. **Diseño del Sistema de IA:** arquitectura de 5 componentes (adquisición e integración de datos, módulo predictivo, manejo de incertidumbre, módulo de decisión y componente de acción) con diagrama de interacciones, monitor de drift y ciclo de retroalimentación.
  5. Métricas de Éxito Compactas (Técnicas, Negocio con fórmula y estimado cuantitativo, y Sociales).
  6. Modelos Mapeados (4 modelos: Regresión Logística, Random Forest, LightGBM y XGBoost).
  7. Estrategia de Monitoreo por **Escenarios de Políticas de Olvido con Ventanas Deslizantes** respaldada en literatura académica (*Gama et al., 2014; Dal Pozzolo et al., 2015*).
  8. Mini Plan de Trabajo y Cronograma de ejecución.

### Código:
```
data/          # dataset IEEE-CIS (raw/ y processed/, no versionados, ver data/README.md)
notebooks/     # 01 EDA temporal · 02 preprocesamiento/features · 03 modelado
               # 04 evaluación temporal · 05 escenarios de concept drift
src/           # módulos reutilizables: data.py, features.py, models.py,
               # evaluation.py, drift.py
figures/       # gráficos exportados para el informe y la infografía
```

**Para ejecutar:**
1. `pip install -r requirements.txt`
2. Descargar el dataset de [Kaggle - IEEE-CIS Fraud Detection](https://www.kaggle.com/c/ieee-fraud-detection/data) y colocar los CSV en `data/raw/` (ver [`data/README.md`](data/README.md)).
3. Correr los notebooks de `notebooks/` en orden (01 → 05).

---

## Documentación Principal
Para consultar la presentación completa para la clase, abre el archivo [`docs/PRESENTACION_PROYECTO1.html`](docs/PRESENTACION_PROYECTO1.html) en tu navegador web.
