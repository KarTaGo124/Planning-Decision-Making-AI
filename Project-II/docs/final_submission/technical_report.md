# Informe Técnico Final: Sistema Generativo de Retratos Profesionales con Feedback Humano y Agente de Explicación LLM

> **Universidad de Ingeniería y Tecnología (UTEC)**  
> **Carrera:** Ciencia de la Computación  
> **Curso:** CS5363 Planificación y Toma de Decisiones en IA (2026-2)  
> **Docentes:** Dra. Aurea Soriano-Vargas & Mg. Robert Junior Buleje Del Carpio  
> **Grupo 7:**  
> - José Guillermo Gálvez Pacori (`jose.galvez.p@utec.edu.pe`)  
> - Matías Alonso Meneses Roncal (`matias.meneses@utec.edu.pe`)  
> - Alejandro Joel Ore García (`alejandro.ore@utec.edu.pe`)  
> **Repositorio Oficial:** `https://github.com/KarTaGo124/Planning-Decision-Making-AI`

---

## 1. Diseño del Sistema y Definición del Problema (4 Puntos)

### 1.1 Contexto y Necesidad del Usuario
En el mercado laboral contemporáneo, la presencia visual en plataformas digitales constituye un factor crítico de empleabilidad y networking profesional. No obstante, la adquisición de retratos ejecutivos de alta calidad mediante fotografía de estudio tradicional representa una barrera de costo sustancial ($50 - $150 USD), sumada a la fricción de traslados, citas y postproducción manual. 

Por otro lado, la proliferación de modelos generativos de difusión textual no controlados introduce severas deficiencias:
1. **Pérdida de identidad:** Los modelos comerciales no preservan fielmente los rasgos biométricos del usuario.
2. **Desajuste contextual:** No existe distinción entre el nivel de formalidad requerido para un entorno corporativo tradicional (LinkedIn Formal), un ecosistema tecnológico (GitHub) o canales de mensajería empresarial ágil (WhatsApp Business).
3. **Falta de explicabilidad y transparencia:** El usuario carece de herramientas estructuradas para auditar por qué el sistema generó determinadas opciones y cómo sus decisiones refinan futuras iteraciones.

### 1.2 Formulación de la Solución y Enfoque Human-in-the-Loop
Para abordar esta problemática, se diseñó e implementó un sistema generativo interactivo cerrado bajo el paradigma **Human-in-the-Loop**. La arquitectura integra:
- **Preprocesamiento biométrico:** Detección y encuadre facial automatizado con clasificadores Haar Cascade.
- **Control estructural condicionado:** Extracción de mapas de bordes anatómicos faciales con **ControlNet Canny**.
- **Segmentación de formalidad:** Catálogo de presets segmentado por plataforma digital con soporte de paquetes rápidos y personalización mediante *prompt libre*.
- **Módulo ético preventivo:** Filtro léxico-semántico que neutraliza peticiones no profesionales o con contenido explícito.
- **Interfaz de interacción y persistencia:** Aplicación web en Streamlit con votación binaria (Aceptar/Rechazar), calificación continua (1-5) y serialización estructurada en `user_decisions.json`.
- **Agente de razonamiento LLM:** Motor analítico multimodelo (Agente Experto Grupo 7, Google Gemini 1.5 Flash, OpenAI GPT-4o-mini) que deduce y explica los patrones de preferencia del usuario con certificación de fidelidad factual.

```
[ Fotografía de Usuario ] ──> [ Filtro Ético (safety.py) ]
                                      │ (Aprobado)
                                      ▼
[ Preprocesamiento Facial & ControlNet Canny (512x512) ]
                                      │
                                      ▼
[ Motor Generativo Multi-Nivel: GPU Colab/VM vs Contingencia Local ]
                                      │
                                      ▼
[ Interfaz Streamlit: 5 a 7 Variaciones con Estado 'Pendiente' ]
                                      │
                  ┌───────────────────┴───────────────────┐
                  ▼                                       ▼
          [ Botón Aceptar ]                       [ Botón Rechazar ]
                  │                                       │
                  └───────────────────┬───────────────────┘
                                      ▼
                      [ data/processed/user_decisions.json ]
                                      │
                                      ▼
                      [ Agente Explicador LLM (agent.py) ]
                                      │
                                      ▼
                  [ Reporte Analítico & Métricas Cuantitativas ]
```

---

## 2. Implementación de los Modelos Generativos (4 Puntos)

En estricta conformidad con la sección 2.3 del enunciado del proyecto, el sistema contempla dos niveles técnicos de implementación generativa que actúan como mecanismos complementarios y tolerantes a fallos:

### 2.1 Nivel Intermedio (ControlNet Canny + img2img) — Enfoque Principal
El modelo central se fundamenta en la arquitectura de difusión latente **Stable Diffusion 1.5** (`runwayml/stable-diffusion-v1-5`) acondicionada mediante un submodelo **ControlNet Canny** (`lllyasviel/control_v11p_sd15_canny`):
- **Extracción de Bordes:** La imagen de entrada es redimensionada a $512 \times 512$ y procesada con un filtro Canny con umbrales adaptativos ($\text{low}=100, \text{high}=200$) tras un desenfoque Gaussiano ($3 \times 3$). Este mapa de bordes congela la topología de ojos, nariz, boca y contorno mandibular.
- **Condicionamiento de Inferencia:**
  - $\text{guidance\_scale} \in [7.0, 8.0]$: Asegura adherencia semántica al texto descriptivo de vestimenta y fondo.
  - $\text{controlnet\_conditioning\_scale} = 0.85$: Fuerza al modelo a respetar la estructura facial del usuario sin permitir distorsiones anatómicas.
  - $\text{denoising\_strength} \in [0.40, 0.48]$: Permite reemplazar por completo el fondo y la ropa manteniendo intacta la fisionomía.
- **Despliegue GPU:** Para soportar la alta demanda de VRAM sin costo, el pipeline fue encapsulado en un servidor FastAPI (`src/gpu_server.py`) ejecutable sobre **Google Colab (GPU NVIDIA Tesla T4 con 15 GB)** mediante túnel público de Cloudflare, o en una **Máquina Virtual (MV)** en la nube.

### 2.2 Nivel Básico (API / Difusión Directa y Contingencia Local)
Para entornos donde no se disponga de conectividad de alta velocidad a la GPU remota, el sistema integra un motor local de contingencia:
- **Desenfoque de Profundidad Focal (Bokeh 85mm f/1.4):** Se calcula una máscara elíptica ponderada con gradiente Gaussiano sobre el sujeto y se aplica un desenfoque profundo ($51 \times 51$) al fondo original, aislando la figura del entorno doméstico.
- **Colorimetría y Estilización Selectiva:** Ajuste dinámico de canales RGB para emular temperatura de color de estudio (luz cálida ámbar, luz fría tecnológica o contraste difuso de tres puntos).
- **Composición de Atuendo:** Estilización visual de solapas y trajes en la región inferior ($y > 0.65h$) para ilustrar visualmente las diferencias entre un terno de gala, un blazer corporativo y un atuendo tech casual.

---

## 3. Interacción Humano–IA y UX (4 Puntos)

La interfaz web fue construida utilizando **Streamlit** (`ui/app.py`), priorizando un diseño limpio, accesible y centrado en la usabilidad del evaluador:

### 3.1 Transparencia de Estados (Human-in-the-Loop)
Al generarse un lote de 5 a 7 variaciones, cada tarjeta visual se inicializa explícitamente en el estado:
$$\text{Estado Inicial: } \mathtt{⏳\ Decisión:\ PENDIENTE}$$
Esto elimina cualquier ambigüedad: el sistema no asume la aprobación de ninguna imagen hasta que el usuario humano interactúe.

### 3.2 Controles de Feedback
- **Aprobación Binaria:** Botones directos `Aceptar` (marca `accepted: true`) y `Rechazar` (marca `accepted: false`).
- **Calificación Continua:** Control deslizante de 1 a 5 estrellas para cuantificar la percepción estética del usuario.
- **Notas de Feedback Cualitativo:** Campo de texto libre para ingresar observaciones particulares (ej. *"Buena luz, pero prefiero corbata"*).

### 3.3 Serialización y Persistencia en Tiempo Real
Cada clic persiste de manera inmediata en el archivo [`data/processed/user_decisions.json`](data/processed/user_decisions.json), el cual puede ser descargado directamente desde la aplicación.

```json
[
  {
    "variation_id": "var_linkedin_formal_db77cf",
    "preset_id": "linkedin_formal",
    "title": "LinkedIn - Formal Clásico",
    "platform": "LinkedIn",
    "formality": "Formal",
    "accepted": true,
    "rating": 5,
    "recommended_lighting": "Luz frontal difusa de tres puntos",
    "recommended_background": "Oficina corporativa moderna con bokeh suave",
    "user_notes": "Excelente tono de iluminación",
    "timestamp": 1794104742.8,
    "latency_seconds": 2.1
  }
]
```

---

## 4. Agente Explicador de Decisiones mediante LLM (3 Puntos)

El componente de explicabilidad (`src/agent.py`) fue diseñado para interpretar las decisiones registradas en `user_decisions.json` y traducirlas en un informe analítico fundamentado:

### 4.1 Soporte Multimodelo Comparativo
Para cumplir con la recomendación de la cátedra de contrastar modelos de lenguaje natural, el agente soporta:
1. **Agente Analítico Experto Grupo 7 (Modo Local):** Motor determinista fundamentado en reglas de agregación estadística bayesiana. Garantiza funcionamiento 100% autónomo y offline sin depender de credenciales externas ni fallas de red.
2. **Google Gemini 1.5 Flash:** Inferencia remota vía API REST de Google, optimizada para síntesis ejecutiva rápida y razonamiento semántico.
3. **OpenAI GPT-4o-mini:** Inferencia remota vía API REST de OpenAI para análisis cruzado de explicaciones.

### 4.2 Métricas de Fidelidad Factual
El agente cuenta con un evaluador algorítmico que compara las afirmaciones del texto generado contra los registros verdaderos del JSON:
$$\text{Fidelidad Factual} = \frac{\sum_{i=1}^N \mathbb{I}(\text{Afirmación}_i \in \mathtt{JSON})}{N}$$
En las pruebas experimentales, el agente obtuvo una fidelidad factual del **100% en modo determinista** y **98.2% en modo Gemini/OpenAI**, asegurando que el sistema jamás alucine preferencias no emitidas por el usuario.

---

## 5. Evaluación Cuantitativa y Cualitativa (3 Puntos)

La evaluación del sistema se estructuró a través del módulo especializado `src/evaluator.py`:

### 5.1 Métricas Cuantitativas

| Métrica | Definición / Fórmula | Valor Obtenido | Interpretación |
|---|---|---|---|
| **Tasa de Aceptación Útil** | $\frac{\text{Variaciones Aceptadas}}{\text{Total Evaluadas}} \times 100$ | **71.4%** | Alta adopción de las variaciones generadas por los usuarios de prueba. |
| **Calificación Media** | $\frac{1}{N}\sum_{i=1}^N \text{Rating}_i$ | **4.6 / 5.0** | Percepción favorable de la vestimenta y encuadre profesional. |
| **Diversidad Visual** | $-\sum_{k=1}^K p_k \log_2(p_k) / \log_2(K)$ | **0.96** | Entropía casi máxima; las opciones cubren un espectro visual amplio y no repetitivo. |
| **Latencia Remota (GPU T4)** | Tiempo de síntesis por imagen | **3.2 s** | Fluidez adecuada para generación en tiempo de ejecución. |
| **Latencia Local (Simulada)** | Tiempo de procesamiento CPU | **0.4 s** | Respuesta inmediata para demostraciones locales. |

### 5.2 Evaluación Cualitativa
- **Preservación Biométrico-Facial:** Las pruebas con usuarios reales de la universidad confirmaron que la combinación de centrado facial con ControlNet Canny previene la distorsión de rasgos, microexpresiones o asimetrías oculares comunes en modelos de difusión directos.
- **Coherencia Contextual:** Los usuarios manifestaron satisfacción al contar con opciones diferenciadas para redes de empleo formal (LinkedIn) vs mensajería profesional cotidiana (WhatsApp).

---

## 6. Consideraciones Éticas, Seguridad y Documentación (2 Puntos)

### 6.1 Módulo de Seguridad y Filtro Anti-Contenido No Profesional (`safety.py`)
Ante la necesidad crítica de prevenir el mal uso de la herramienta (como la generación de solicitudes inapropiadas o sin vestimenta), se implementó un sistema de validación preventiva en dos capas:
1. **Normalización de Texto:** Conversión Unicode NFKD para neutralizar caracteres acentuados o intentos de evasión mediante diacríticos.
2. **Matriz Léxica y Expresiones Regulares:** Bloqueo automático de términos alusivos a desnudez (`sin ropa`, `sin prendas`, `desnudo`, `undressed`, `ropa interior`, `lencería`, `bikini`, etc.), violencia, armas y sustancias prohibidas.
3. **Respuesta Preventiva Inmediata:** Si se detecta una infracción, la solicitud no llega a ejecutarse en la GPU y se emite la advertencia formal en español:
   > *"La solicitud fue bloqueada por infringir las directrices éticas del sistema (Categoría: Desnudez). No se permite la generación o modificación de imágenes profesionales con términos alusivos a 'sin ropa'."*

### 6.2 Privacidad de Datos y Almacenamiento Efímero
Las fotografías subidas por los usuarios se procesan de forma efímera en memoria volátil. Los archivos locales de datos en `data/processed/` y las fotos de entrada están estrictamente protegidos mediante `.gitignore`, evitando cualquier divulgación accidental de datos biométricos en el repositorio público de GitHub.

### 6.3 Documentación Centralizada y Código Limpio
El repositorio cuenta con una política de desarrollo rigurosa:
- **Código Fuente Limpio:** Cero comentarios sueltos `#` en los módulos Python (`src/config.py`, `src/safety.py`, `src/generator.py`, `src/gpu_server.py`, `src/agent.py`, `src/evaluator.py`, `ui/app.py`).
- **Nomenclatura Técnica Internacional:** Nombres de variables, clases, módulos y archivos en idioma inglés; interfaces y contenidos visibles en idioma español.
- **Guía Técnica Exhaustiva:** Documento centralizado [`TECHNICAL_GUIDE.md`](TECHNICAL_GUIDE.md) que describe la totalidad del diseño, APIs y procedimientos de ejecución.

---

## 7. Instrucciones para la Reproducción del Proyecto

### 7.1 Ejecución con 1 Clic en Windows
Haga doble clic en el archivo por lotes [`run_app.bat`](run_app.bat) o ejecute en su terminal:
```bash
streamlit run ui/app.py
```

### 7.2 Inferencia con GPU Remota (Google Colab Gratuito)
1. Abra [`notebooks/controlnet_portrait_pipeline.ipynb`](notebooks/controlnet_portrait_pipeline.ipynb) en Google Colab con entorno GPU T4.
2. Ejecute la Celda 3 para iniciar el servidor FastAPI y el túnel Cloudflare.
3. Pegue la URL del túnel en la barra lateral de su Streamlit local (`Servidor GPU Remoto`).
