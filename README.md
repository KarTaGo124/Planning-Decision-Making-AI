# Planificación y Toma de Decisiones en IA — UTEC (2026-2)

Repositorio oficial para el desarrollo de los proyectos de la asignatura **Planificación y Toma de Decisiones en IA** en la Universidad de Ingeniería y Tecnología (UTEC).

* **Docentes:** Dra. Aurea Soriano-Vargas & Mg. Robert Buleje  
* **Institución:** Departamento de Ciencia de la Computación, UTEC  

---

## 📂 Estructura General del Repositorio

El repositorio se organiza de forma modular, alojando cada proyecto del curso en su propio directorio con documentación, código y artefactos independientes:

```text
Planning-Decision-Making-AI/
├── README.md                      # Índice general del repositorio y resumen de proyectos
├── .gitignore                     # Configuración de exclusiones de Git para datos pesados y artefactos
│
├── Project-I/                     # Proyecto 1: Sistema Inteligente Adaptativo con Datos No Estacionarios
│   ├── README.md                  # Documentación detallada y guía de ejecución de Proyecto 1
│   ├── data/                      # Dataset IEEE-CIS (instrucciones de descarga en data/README.md)
│   ├── docs/                      # Informe técnico (PDF/LaTeX), infografía y presentación
│   ├── figures/                   # Gráficos de EDA, degradación temporal y comparación de modelos
│   ├── notebooks/                 # Pipelines en Jupyter (01 a 06: EDA, features, modelado, drift)
│   ├── src/                       # Módulos Python reutilizables (data, features, models, evaluation, drift)
│   ├── pyproject.toml             # Configuración de entorno y dependencias (uv)
│   └── uv.lock                    # Bloqueo de versiones reproducible
│
└── Project-II/                    # Proyecto 2: Sistema Generativo Interactivo con Feedback Humano y Agentes LLM
    ├── README.md                  # Documentación técnica, niveles y rúbrica de Proyecto 2
    ├── docs/                      # Guía oficial del proyecto (Evaluacion_Proyecto2.pdf)
    ├── data/                      # Datasets e imágenes de entrada (raw/ y processed/)
    ├── notebooks/                 # Prototipado generativo y experimentación
    ├── src/                       # Módulos del generador, agente LLM y métricas
    └── ui/                        # Interfaz gráfica interactiva (Human-in-the-Loop)
```

---

## 🎯 Proyectos del Curso

### 💳 [Proyecto 1: Sistema Inteligente Adaptativo con Datos No Estacionarios](Project-I/)
* **Caso de Uso:** Detección de fraude financiero en comercio electrónico bajo deriva de concepto (*Concept Drift*).
* **Dataset:** IEEE-CIS Fraud Detection (Kaggle).
* **Aspectos Clave:**
  * División estrictamente cronológica de datos (`TransactionDT`) para evitar fuga de información (*data leakage*).
  * Comparación de cuatro modelos: dos tradicionales (Regresión Logística, Random Forest) y dos avanzados basados en *Gradient Boosting* (LightGBM, XGBoost).
  * Optimización de umbral de decisión basada en costo económico real (fraude omitido vs. fricción por falso positivo).
  * Monitoreo y mitigación del drift mediante **políticas de olvido basadas en ventanas deslizantes** y ponderación por recencia (*time-decay*).
  * Análisis de equidad social (*Fairness*) en la tasa de rechazo por rangos de monto de transacción.
* **Entregables:** Código reproducible (gestionado con `uv`), informe técnico de 8 páginas ([`Project-I/docs/informe_tecnico.pdf`](Project-I/docs/informe_tecnico.pdf)), infografía del ciclo de vida ([`Project-I/docs/infografia.pdf`](Project-I/docs/infografia.pdf)) y presentación interactiva ([`Project-I/docs/PRESENTACION_PROYECTO1.html`](Project-I/docs/PRESENTACION_PROYECTO1.html)).

👉 *Consulta la documentación completa en el [README de Project-I](Project-I/README.md).*

---

### 🎨 [Proyecto 2: Sistema Generativo Interactivo para Variaciones Visuales con Feedback Humano y Explicación mediante Agentes de IA](Project-II/)
* **Caso de Uso:** Sistema generativo interactivo con el ser humano en el ciclo de decisión (*Human-in-the-Loop*).
* **Guía Oficial:** [`Project-II/docs/Evaluacion_Proyecto2.pdf`](Project-II/docs/Evaluacion_Proyecto2.pdf).
* **Aspectos Clave:**
  * **Módulo Generativo:** Generación de exactamente **cinco (5) variaciones visuales** a partir de una imagen de entrada cargada por el usuario (e.g., modificando iluminación, expresión, estilo o composición).
  * **Interfaz Gráfica y Feedback:** Visualización interactiva donde el usuario evalúa, acepta o rechaza individualmente cada variación, registrando las decisiones de manera estructurada.
  * **Agente Basado en LLMs:** Generación automatizada de un resumen y explicación textual coherente que describe y justifica fielmente las opciones aceptadas y rechazadas.
  * **Evaluación Multicriterio:** Calidad visual, diversidad de variaciones, coherencia explicativa del agente y usabilidad del sistema.
  * **Reflexión Ética:** Análisis sobre manipulación de identidad visual, sesgos en datos/modelos y uso responsable.
* **Entregables:** Código fuente del sistema integrado (Generador + UI + Agente LLM), informe técnico de máximo 5 páginas, soporte visual y demostración en vivo o en video.

👉 *Consulta los requisitos, niveles técnicos y rúbrica en el [README de Project-II](Project-II/README.md).*

---

## 🛠️ Requisitos y Herramientas

* **Lenguaje:** Python 3.11+
* **Gestor de Entorno y Paquetes:** [`uv`](https://github.com/astral-sh/uv)
* **Control de Versiones:** Git & GitHub
