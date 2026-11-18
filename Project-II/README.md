# Proyecto 2: Sistema Generativo Interactivo para Variaciones Visuales con Feedback Humano y Explicación mediante Agentes de IA

**Curso:** CS5363 Planificación y Toma de Decisiones en IA — UTEC (2026-2)  
**Profesores:** Dra. Aurea Soriano-Vargas & Mg. Robert Junior Buleje Del Carpio  
**Grupo 7:**  
- José Guillermo Gálvez Pacori (`jose.galvez.p@utec.edu.pe`)  
- Matías Alonso Meneses Roncal (`matias.meneses@utec.edu.pe`)  
- Alejandro Joel Ore García (`alejandro.ore@utec.edu.pe`)  

**Caso de uso:** retratos profesionales para LinkedIn, WhatsApp corporativo y GitHub, generados a partir de una foto del usuario.
**Formas de generar:**
- **Nivel Intermedio:** Stable Diffusion 1.5 + ControlNet Canny en modo img2img.
- **Nivel Básico:** Stable Diffusion 1.5 img2img sin ControlNet.

Ambas usan el LoRA público detail-tweaker y corren en una GPU T4 de Google Colab. La interfaz es Streamlit y el agente explicador usa Gemini o un agente de reglas.

---

## 1. Documentación y entregables

* **Cómo ejecutar:** [`HOW_TO_RUN.md`](HOW_TO_RUN.md) (Colab, Windows con 1 clic y máquina virtual).
* **Entrega final:** carpeta [`entregable/`](entregable/), con el informe en PDF, la presentación y `ENTREGA.txt`.
* **Material de preparación:** [`material_apoyo/`](material_apoyo/), con la fuente del informe, el guion de la exposición y el guion del video.
* **Guía técnica del código:** [`TECHNICAL_GUIDE.md`](TECHNICAL_GUIDE.md).
* **Enunciado Oficial:** [`docs/guidelines/project_2_statement.pdf`](docs/guidelines/project_2_statement.pdf)
* **Rúbrica Oficial de Evaluación:** [`docs/guidelines/project_2_rubric.pdf`](docs/guidelines/project_2_rubric.pdf)
* **Historial de Avance 1:** [`docs/submission_1/`](docs/submission_1/)

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
│   ├── final_submission/          # Apunta a entregable/
│   ├── guidelines/                # Enunciado, rúbrica e indicaciones del docente
│   └── submission_1/              # Entregable del avance
│
├── entregable/                    # Entrega final: informe PDF, presentación y ENTREGA.txt
├── material_apoyo/                # Fuente del informe, scripts de métricas y figuras, guiones
│
├── notebooks/
│   └── controlnet_portrait_pipeline.ipynb # Servidor GPU y experimentos en Google Colab ("Ejecutar todas")
│
├── src/
│   ├── config.py                  # Catálogo de estilos y paquetes
│   ├── safety.py                  # Filtro ético previo a la generación
│   ├── generator.py               # Preproceso facial, cliente del servidor GPU y contingencia local
│   ├── diffusion.py               # SD 1.5 + ControlNet Canny / img2img + LoRA
│   ├── gpu_server.py              # Servidor FastAPI para la GPU
│   ├── agent.py                   # Agente explicador (Gemini, OpenAI, reglas)
│   └── evaluator.py               # Fidelidad de la explicación y métricas de sesión
│
└── ui/
    └── app.py                     # Aplicación web interactiva en Streamlit (Human-in-the-Loop)
```

---

## 3. Instrucciones de Ejecución

### Opción A: Ejecución Rápida con 1 Clic (Windows)
Haga doble clic en el archivo [`run_app.bat`](run_app.bat).

### Opción B: Ejecución en Terminal
```bash
cd Project-II
pip install -r requirements.txt
streamlit run ui/app.py
```

### Opción C: Inferencia con GPU T4 Gratuita en Google Colab
1. Suba [`notebooks/controlnet_portrait_pipeline.ipynb`](notebooks/controlnet_portrait_pipeline.ipynb) a Google Colab.
2. Elija GPU T4 en Entorno de ejecución > Cambiar tipo de entorno de ejecución.
3. Use Entorno de ejecución > Ejecutar todas y suba una foto cuando el notebook la pida. Al terminar, se descarga `resultados_colab.zip` y aparece una URL `trycloudflare.com`.
4. En la app de Streamlit, elija "Nivel Intermedio" o "Nivel Básico", pegue la URL y presione "Probar conexión".
5. Presione "Generar variaciones".
