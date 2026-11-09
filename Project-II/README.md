# Proyecto 2: Sistema Generativo Interactivo para Variaciones Visuales con Feedback Humano y Explicación mediante Agentes de IA

**Curso:** CS5363 Planificación y Toma de Decisiones en IA — UTEC (2026-2)  
**Profesores:** Dra. Aurea Soriano-Vargas & Mg. Robert Junior Buleje Del Carpio  
**Grupo 7:**  
- José Guillermo Gálvez Pacori (`jose.galvez.p@utec.edu.pe`)  
- Matías Alonso Meneses Roncal (`matias.meneses@utec.edu.pe`)  
- Alejandro Joel Ore García (`alejandro.ore@utec.edu.pe`)  

**Caso de Uso Seleccionado:** Asistente Interactivo de Retratos Profesionales Multiplataforma (LinkedIn, WhatsApp Corporativo, GitHub)  
**Nivel Técnico Principal:** Nivel Intermedio (ControlNet Canny + *img2img* + Agente Explicador LLM + Interfaz Gráfica Streamlit)  
**Nivel Técnico de Respaldo:** Nivel Básico (API Preentrenada / Difusión Directa y Contingencia Local)  

---

## 1. Documentación Central y Entregables Oficiales

### 🚀 Guía de Ejecución Rápida
* ⚡ **Guía Completa de Cómo Correr Todo:** Consulte [`HOW_TO_RUN.md`](HOW_TO_RUN.md) para el paso a paso detallado de ejecución en **Google Colab (GPU Gratis)**, **Windows con 1 clic (`run_app.bat`)**, o **Máquina Virtual (MV en la nube)**, además del guión para la sustentación frente al profesor.

### 🌟 Entregable Final (Sustentación del Proyecto)
* 📊 **Diapositivas Interactivas de Sustentación:** [`docs/final_submission/presentation.html`](docs/final_submission/presentation.html) *(Diseño moderno en modo oscuro con navegación por teclado y soporte para impresión PDF).*
* 🎙️ **Guión de Exposición Oral:** [`docs/final_submission/presentation_script.md`](docs/final_submission/presentation_script.md) *(Guión detallado diapositiva por diapositiva en tono natural de estudiante).*
* 📝 **Informe Técnico Final (Rúbrica 20 Pts):** [`docs/final_submission/technical_report.md`](docs/final_submission/technical_report.md) *(Documento exhaustivo cubriendo los 6 criterios de evaluación).*
* 📑 **Diapositivas en Formato Markdown:** [`docs/final_submission/presentation.md`](docs/final_submission/presentation.md)

### 📖 Guías Técnicas y Materiales del Curso
* 📘 **Guía Técnica Integral:** [`TECHNICAL_GUIDE.md`](TECHNICAL_GUIDE.md) *(Documentación exhaustiva de arquitectura, catálogo de presets, seguridad y métricas).*
* 📋 **Enunciado Oficial:** [`docs/guidelines/project_2_statement.pdf`](docs/guidelines/project_2_statement.pdf)
* 📊 **Rúbrica Oficial de Evaluación:** [`docs/guidelines/project_2_rubric.pdf`](docs/guidelines/project_2_rubric.pdf)
* 📦 **Historial de Avance 1:** [`docs/submission_1/`](docs/submission_1/)

---

## 2. Estructura del Proyecto

```text
Project-II/
├── README.md                      # Resumen ejecutivo y guía rápida
├── HOW_TO_RUN.md                  # Guía paso a paso de ejecución (Colab, Local, VM)
├── TECHNICAL_GUIDE.md             # Guía técnica integral y centralizada
├── requirements.txt               # Dependencias Python
├── run_app.bat                    # Lanzador rápido con 1 clic para Windows
│
├── data/
│   ├── raw/                       # Retratos base de entrada (privados, protegidos por git)
│   └── processed/
│       └── user_decisions.json    # Registro de feedback humano serializado en tiempo real
│
├── docs/
│   ├── final_submission/          # Entregables de la sustentación final
│   │   ├── presentation.html      # Diapositivas interactivas
│   │   ├── presentation.md        # Diapositivas en markdown
│   │   ├── presentation_script.md # Guión de exposición oral
│   │   └── technical_report.md    # Informe técnico final
│   ├── guidelines/                # Enunciado y rúbrica oficial de la cátedra
│   └── submission_1/              # Entregable histórico del avance inicial
│
├── notebooks/
│   └── controlnet_portrait_pipeline.ipynb # Notebook para Google Colab con GPU T4 y túnel Cloudflare
│
├── src/                           # Código fuente limpio (Cero comentarios inline #)
│   ├── __init__.py
│   ├── config.py                  # Catálogo de presets de red social, formalidad y prompts
│   ├── safety.py                  # Filtro ético léxico-semántico (bloqueo preventivo)
│   ├── generator.py               # Motor generativo (ControlNet, API y contingencia local)
│   ├── gpu_server.py              # Servidor backend FastAPI para inferencia remota con GPU
│   ├── agent.py                   # Agente explicador de decisiones multimodelo (LLM)
│   └── evaluator.py               # Métricas de tasa de aceptación, diversidad y fidelidad
│
└── ui/
    └── app.py                     # Aplicación web interactiva en Streamlit (Human-in-the-Loop)
```

---

## 3. Instrucciones de Ejecución

### Opción A: Ejecución Rápida con 1 Clic (Windows)
Simplemente haga doble clic en el archivo [`run_app.bat`](run_app.bat).

### Opción B: Ejecución en Terminal
```bash
cd Project-II
pip install -r requirements.txt
streamlit run ui/app.py
```

### Opción C: Inferencia Fotorrealista con GPU T4 Gratuita en Google Colab
1. Abra [`notebooks/controlnet_portrait_pipeline.ipynb`](notebooks/controlnet_portrait_pipeline.ipynb) en **Google Colab**.
2. Active la GPU gratuita en *Entorno de ejecución > Cambiar tipo de entorno > T4 GPU*.
3. Ejecute la Celda 3 para iniciar el servidor FastAPI y el túnel Cloudflare.
4. En su aplicación local de Streamlit, seleccione en la barra lateral el modo **"Servidor GPU Remoto (Google Colab / MV)"**, pegue la URL generada y presione **"🔌 Probar Conexión GPU"**.
5. ¡Listo! La generación fotorrealista correrá en la GPU de Google Colab en 3 segundos por foto.
