# Proyecto 2: Sistema Generativo Interactivo para Variaciones Visuales con Feedback Humano y Explicación mediante Agentes de IA

**Curso:** CS5363 Planificación y Toma de Decisiones en IA — UTEC (2026-2)  
**Profesores:** Dra. Aurea Soriano-Vargas & Mg. Robert Junior Buleje Del Carpio  
**Grupo 7:**  
- José Guillermo Gálvez Pacori  
- Matías Alonso Meneses Roncal  
- Alejandro Joel Ore García  

**Caso de Uso Seleccionado:** Asistente Interactivo de Edición y Estilizado de Retratos Profesionales  
**Nivel Técnico Principal:** Nivel Intermedio (ControlNet Canny + *img2img* + Agente Explicador LLM + Interfaz Gráfica Streamlit)  
**Nivel Técnico de Respaldo:** Nivel Básico (API Preentrenada / Difusión Directa)  

---

## 1. Documentación Central y Enlaces de Interés

* 📖 **Guía Técnica Centralizada:** Consulte [`TECHNICAL_GUIDE.md`](TECHNICAL_GUIDE.md) para la explicación exhaustiva de la arquitectura, modelos, presets, filtros de seguridad y métricas.
* 📋 **Enunciado Oficial:** [`docs/guidelines/project_2_statement.pdf`](docs/guidelines/project_2_statement.pdf)
* 📊 **Rúbrica Oficial de Evaluación:** [`docs/guidelines/project_2_rubric.pdf`](docs/guidelines/project_2_rubric.pdf)
* 🚀 **Entregable 1 (Avance del Proyecto):**
  - Diapositivas interactivas: [`docs/submission_1/presentation.html`](docs/submission_1/presentation.html)
  - Versión para impresión PDF: [`docs/submission_1/presentation.pdf`](docs/submission_1/presentation.pdf)
  - Documento técnico: [`docs/submission_1/presentation.md`](docs/submission_1/presentation.md)
  - Guión de exposición: [`docs/submission_1/presentation_script.md`](docs/submission_1/presentation_script.md)

---

## 2. Estructura del Proyecto

```text
Project-II/
├── README.md                      # Resumen del proyecto e instrucciones básicas
├── TECHNICAL_GUIDE.md             # Guía técnica integral y centralizada
├── requirements.txt               # Dependencias Python
│
├── data/
│   ├── raw/                       # Retratos base de entrada
│   └── processed/
│       └── decisiones_usuario.json # Registro de feedback humano estructurado
│
├── docs/
│   ├── guidelines/                # Enunciado y rúbrica oficial del curso
│   └── submission_1/              # Materiales del primer avance presentado
│
├── src/                           # Código fuente limpio (sin comentarios en línea)
│   ├── __init__.py
│   ├── config.py                  # Presets de plataformas, formalidad y prompts
│   ├── safety.py                  # Filtro ético y validación de restricciones
│   ├── generator.py               # Motor generativo (Niveles Intermedio y Básico)
│   ├── agent.py                   # Agente explicador de decisiones (LLM)
│   └── evaluator.py               # Métricas cuantitativas y cualitativas
│
└── ui/
    └── app.py                     # Interfaz web interactiva en Streamlit
```

---

## 3. Instrucciones Rápidas de Ejecución

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Ejecutar la interfaz interactiva:**
   ```bash
   streamlit run ui/app.py
   ```

3. **Flujo de uso en la interfaz:**
   - Suba una foto de retrato o utilice la imagen sintética de demostración.
   - Seleccione el nivel técnico (`Nivel Intermedio` o `Nivel Básico`) y el paquete de variaciones (`Paquete Corporativo`, `Paquete Tech` o `Paquete Ejecutivo`).
   - Opcionalmente agregue especificaciones en el *prompt libre*.
   - Haga clic en **Generar Variaciones Visuales**.
   - Evalúe cada alternativa generada presionando **Aceptar** o **Rechazar**, asignando puntajes (1-5 estrellas) y notas.
   - Haga clic en **Generar Explicación con Agente IA** para obtener un reporte analítico del comportamiento y descargar el registro `decisiones_usuario.json`.
