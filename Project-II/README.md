# Proyecto 2: Sistema Generativo Interactivo para Variaciones Visuales con Feedback Humano y Explicación mediante Agentes de IA

**Curso:** Planificación y Toma de Decisiones en IA — UTEC (2026-2)  
**Profesor:** Dra. Aurea Soriano-Vargas  
**Documento Oficial:** [`docs/Evaluacion_Proyecto2.pdf`](docs/Evaluacion_Proyecto2.pdf)

---

## 1. Descripción del Proyecto

A diferencia de los enfoques tradicionales de inteligencia artificial centrados exclusivamente en la predicción estática, los sistemas generativos modernos plantean nuevos retos en control del proceso creativo, toma de decisiones y confiabilidad.

Este proyecto aborda el diseño e implementación de un **sistema generativo interactivo con el ser humano en el ciclo de decisión (Human-in-the-Loop)**. El sistema produce variaciones visuales a partir de una imagen de entrada proporcionada por el usuario, integra explícitamente su retroalimentación mediante una interfaz gráfica y utiliza un **agente basado en modelos de lenguaje (LLM)** para sintetizar y explicar de forma coherente las decisiones de selección tomadas.

---

## 2. Requisitos Principales del Sistema

1. **Módulo Generativo:** Producir exactamente **cinco (5) variaciones visuales** a partir de una imagen de entrada cargada por el usuario (e.g., modificando iluminación, expresión, estilo, atributos faciales o composición).
2. **Interfaz Gráfica e Interacción Humano-IA:** Visualizar de forma clara las cinco opciones generadas y registrar estructuradamente la decisión del usuario (aceptar o rechazar cada alternativa).
3. **Agente Explicativo (LLM):** Generar un resumen y explicación textual coherente que describa fielmente qué opciones fueron aceptadas y cuáles rechazadas, sustentando el proceso de selección.
4. **Métricas y Evaluación:** Evaluar calidad visual, diversidad de variaciones, fidelidad/coherencia de las explicaciones del agente y usabilidad del sistema.
5. **Consideraciones Éticas:** Análisis explícito sobre manipulación de identidad visual, presencia de sesgos y uso responsable de datos.

---

## 3. Niveles de Implementación Técnica

El proyecto contempla tres niveles de complejidad según el diseño del módulo generativo:

| Nivel | Descripción y Tecnologías Sugeridas |
| :--- | :--- |
| **Básico** | Uso de modelos generativos preentrenados o APIs (e.g., Stable Diffusion vía API, DALL-E) para producir variaciones a partir de la imagen de entrada. |
| **Intermedio** | Uso de modelos generativos controlables o técnicas de transformación de imágenes para modificar atributos específicos (e.g., Stable Diffusion con *img2img*, ControlNet, InstructPix2Pix). |
| **Avanzado** | Implementación o adaptación de modelos generativos propios o arquitecturas de traducción imagen a imagen (e.g., variantes de GANs como DCGAN/StyleGAN, modelos de difusión propios, pix2pix, CycleGAN, ControlNet ajustado). |

---

## 4. Estructura del Directorio `Project-II/`

```text
Project-II/
├── README.md              # Documentación técnica y guía de inicio del Proyecto 2
├── docs/
│   └── Evaluacion_Proyecto2.pdf   # Guía y rúbrica oficial de la cátedra
├── data/
│   ├── raw/               # Imágenes o datasets base de entrada (no versionados pesados)
│   └── processed/         # Imágenes preprocesadas o generadas
├── notebooks/             # Cuadernos de experimentación generativa y prototipado
├── src/                   # Módulos Python reutilizables
│   ├── __init__.py
│   ├── generator.py       # Módulo generativo de variaciones visuales (5 opciones)
│   ├── agent.py           # Agente LLM para síntesis y explicación de decisiones
│   └── evaluation.py      # Métricas de calidad, diversidad y coherencia
└── ui/                    # Interfaz gráfica interactiva (Streamlit, Gradio o Web)
```

---

## 5. Productos Esperados y Entregables

* **Código del Sistema:** Pipeline generativo completo, interfaz gráfica funcional, almacenamiento de decisiones y agente LLM.
* **Documento Técnico:** Informe de un **máximo de 5 páginas** describiendo el problema, la arquitectura, el modelo generativo, la interfaz, los resultados y la reflexión ética.
* **Elementos Visuales:** Diagramas de arquitectura, flujo de información/decisión y capturas de ejemplos e interacción.
* **Demostración del Sistema:** Demostración en vivo o video evidenciando la generación de las 5 opciones, la interacción del usuario y la explicación automática del agente.

---

## 6. Rúbrica de Evaluación (20 Puntos)

| Criterio | Descripción | Puntos |
| :--- | :--- | :---: |
| **Diseño del sistema** | Claridad en la definición del problema, coherencia del diseño general e integración de componentes. | **4** |
| **Modelo generativo** | Calidad y diversidad de las imágenes generadas, correcta implementación y análisis del comportamiento. | **4** |
| **Interacción humano–IA** | Funcionalidad y usabilidad de la interfaz, claridad en visualización y registro adecuado de decisiones. | **4** |
| **Explicabilidad** | Coherencia y calidad del resumen del agente LLM, alineación con las decisiones del usuario. | **3** |
| **Evaluación y análisis** | Uso adecuado de métricas, análisis crítico, identificación de limitaciones y mejoras. | **3** |
| **Aspectos éticos y documentación** | Reflexión ética relevante, calidad del informe técnico (máx. 5 págs) y soporte visual adecuado. | **2** |
| **Total** | | **20** |
