# Planificación y Toma de Decisiones en IA — UTEC (2026-2)

Este repositorio contiene la propuesta y avances para los proyectos de la asignatura **Planificación y Toma de Decisiones en IA** en la Universidad de Ingeniería y Tecnología (UTEC), dictada por la **Dra. Aurea Soriano-Vargas** y el **Mg. Robert Buleje**.

---

## Proyecto 1: Sistema Inteligente Adaptativo con Datos No Estacionarios

Se presenta la formulación contextualizada del problema, la selección del conjunto de datos, los objetivos y restricciones del sistema, el diseño de su arquitectura y la estrategia de monitoreo temporal por escenarios para la **detección de fraude financiero en e-commerce**.

### Contenido:
* **Presentación Interactiva:** [`PRESENTACION_PROYECTO1.html`](PRESENTACION_PROYECTO1.html)
* **Documento Técnico de Apoyo:** [`PRESENTACION_PROYECTO1.md`](PRESENTACION_PROYECTO1.md)
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

---

## Documentación Principal
Para consultar la presentación completa para la clase, abre el archivo [`PRESENTACION_PROYECTO1.html`](PRESENTACION_PROYECTO1.html) en tu navegador web.
