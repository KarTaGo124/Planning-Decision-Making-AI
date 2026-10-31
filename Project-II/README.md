# Proyecto 2: Sistema Generativo Interactivo para Variaciones Visuales con Feedback Humano y Explicación mediante Agentes de IA

**Curso:** Planificación y Toma de Decisiones en IA — UTEC (2026-2)  
**Profesores:** Dra. Aurea Soriano-Vargas & Mg. Robert Buleje  
**Caso de Uso Seleccionado:** Asistente Interactivo de Edición y Estilizado de Retratos Profesionales  
**Nivel Técnico Elegido:** Nivel Intermedio (Stable Diffusion con *img2img* / ControlNet + Agente LLM + Interfaz Gráfica)  

---

## 1. Documentación del Proyecto

* **Presentación de Avance (Diapositivas HTML):** [`docs/PRESENTACION_AVANCE_PROYECTO2.html`](docs/PRESENTACION_AVANCE_PROYECTO2.html)
* **Documento Técnico de Avance (Markdown):** [`docs/PRESENTACION_AVANCE_PROYECTO2.md`](docs/PRESENTACION_AVANCE_PROYECTO2.md)
* **Guía Oficial de la Cátedra:** [`docs/Evaluacion_Proyecto2.pdf`](docs/Evaluacion_Proyecto2.pdf)

---

## 2. Descripción del Proyecto

A diferencia de los enfoques tradicionales de inteligencia artificial centrados exclusivamente en la predicción estática, los sistemas generativos modernos plantean nuevos retos en control del proceso creativo, toma de decisiones y confiabilidad.

Este proyecto aborda el diseño e implementación de un **sistema generativo interactivo con el ser humano en el ciclo de decisión (Human-in-the-Loop)**. A partir de una fotografía de retrato provista por el usuario, el sistema:
1. Genera exactamente **cinco (5) variaciones visuales controladas** (iluminación de estudio, expresión, fondo contextual, vestimenta formal y estilo editorial) preservando la identidad facial.
2. Permite al usuario evaluar visualmente las alternativas en una **interfaz gráfica** y registrar de manera estructurada su decisión (Aceptar o Rechazar cada opción).
3. Utiliza un **agente basado en modelos de lenguaje (LLM)** para interpretar el registro de elecciones y generar automáticamente un resumen explicativo coherente, estructurado y transparente en lenguaje natural.

---

## 3. Requisitos Principales del Sistema

* **Módulo Generativo Controlable (Nivel Intermedio):** Stable Diffusion acondicionado con *img2img* y ControlNet para modificar atributos específicos garantizando la preservación biométrica del sujeto.
* **Interfaz Gráfica e Interacción Humano-IA:** Visualización comparativa clara con controles binarios de decisión para cada alternativa y almacenamiento estructurado en formato JSON.
* **Agente Explicativo (LLM):** Generación de explicaciones que sustentan de forma fiel qué opciones fueron aceptadas y cuáles rechazadas.
* **Métricas Multicriterio:** Calidad semántica (CLIP-Score), diversidad visual (LPIPS), tasa de aceptación útil, latencia de inferencia y coherencia factual del agente.
* **Consideraciones Éticas:** Tratamiento efímero y privado de imágenes personales, auditoría de sesgos algorítmicos y prevención de suplantación de identidad.

---

## 4. Estructura del Directorio `Project-II/`

```text
Project-II/
├── README.md                      # Documentación técnica y guía de inicio del Proyecto 2
├── docs/
│   ├── Evaluacion_Proyecto2.pdf   # Guía y rúbrica oficial de la cátedra
│   ├── PRESENTACION_AVANCE_PROYECTO2.html # Presentación interactiva en diapositivas (Checkpoint 1)
│   └── PRESENTACION_AVANCE_PROYECTO2.md   # Documento técnico de apoyo del avance
├── data/
│   ├── raw/                       # Imágenes base o dataset de referencia (CelebA-HQ)
│   └── processed/                 # Imágenes preprocesadas o generadas
├── notebooks/                     # Cuadernos de experimentación generativa y prototipado
├── src/                           # Módulos Python reutilizables
│   ├── __init__.py
│   ├── generator.py               # Módulo generativo de 5 variaciones (SD + ControlNet)
│   ├── agent.py                   # Agente LLM para síntesis y explicación de decisiones
│   └── evaluation.py              # Métricas de calidad, diversidad y coherencia
└── ui/                            # Interfaz gráfica interactiva (Human-in-the-Loop)
```

---

## 5. Rúbrica de Evaluación Oficial (20 Puntos)

| Criterio | Descripción | Puntos |
| :--- | :--- | :---: |
| **Diseño del sistema** | Claridad en la definición del problema, coherencia del diseño general e integración de componentes. | **4** |
| **Modelo generativo** | Calidad y diversidad de las imágenes generadas, correcta implementación y análisis del comportamiento. | **4** |
| **Interacción humano–IA** | Funcionalidad y usabilidad de la interfaz, claridad en visualización y registro adecuado de decisiones. | **4** |
| **Explicabilidad** | Coherencia y calidad del resumen del agente LLM, alineación con las decisiones del usuario. | **3** |
| **Evaluación y análisis** | Uso adecuado de métricas, análisis crítico, identificación de limitaciones y mejoras. | **3** |
| **Aspectos éticos y documentación** | Reflexión ética relevante, calidad del informe técnico (máx. 5 págs) y soporte visual adecuado. | **2** |
| **Total** | | **20** |
