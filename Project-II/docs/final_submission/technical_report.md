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
En el mercado laboral actual, la presencia visual en plataformas digitales constituye un factor crítico de empleabilidad y networking profesional. No obstante, la adquisición de retratos ejecutivos de calidad mediante fotografía de estudio tradicional representa una barrera de costo sustancial ($50 - $150 USD), sumada a la fricción de traslados, citas y postproducción manual. 

Por otro lado, la proliferación de modelos generativos de difusión textual no controlados introduce severas deficiencias:
1. **Pérdida de identidad:** Los modelos comerciales convencionales no preservan fielmente los rasgos biométricos del usuario.
2. **Desajuste contextual:** No existe distinción entre el nivel de formalidad requerido para un entorno corporativo tradicional (LinkedIn Formal), un ecosistema tecnológico (GitHub) o canales de mensajería empresarial ágil (WhatsApp Business).
3. **Falta de explicabilidad y transparencia:** El usuario carece de herramientas estructuradas para auditar por qué el sistema generó determinadas opciones y cómo sus decisiones refinan futuras iteraciones.

### 1.2 Integración del Taller de Design Thinking (Semana 13)
Siguiendo la metodología del taller de Design Thinking impartido en la Semana 13 por la Diseñadora Industrial Andrea Alarcón, el equipo abordó el desarrollo del dataproducto centrado estrictamente en las personas:

* **Enmarcar el Reto (Pregunta Guía):**  
  *¿Cómo podríamos facilitar la generación accesible, contextualizada y controlada de retratos profesionales para estudiantes y jóvenes profesionales de UTEC, garantizando que su identidad facial se mantenga inalterada?*
* **Perfil de Usuario (Arquetipo UTEC):**
  - *Ocupación:* Estudiante de ciclos avanzados / egresado reciente en búsqueda de prácticas preprofesionales o empleo formal.
  - *Frustraciones:* Presupuesto limitado para sesiones de fotos, temor a que las herramientas de IA generen imágenes artificiales o deformes, y desconocimiento de los códigos visuales de cada red.
  - *Motivaciones:* Proyectar solvencia técnica y liderazgo sin perder autenticidad fisionómica.
* **Propuesta de Valor en Tres Dimensiones:**
  - *Dimensión Funcional:* Generación automatizada de 5 a 7 variaciones con presets predefinidos (iluminación, vestimenta, encuadre $512 \times 512$) y posibilidad de ajuste fino mediante *prompt libre*.
  - *Dimensión Social:* Proyección de credibilidad y adecuación ante reclutadores en LinkedIn y clientes en WhatsApp corporativo.
  - *Dimensión Emocional:* Sensación de seguridad y confianza personal al constatar que los rasgos biométricos permanecen intactos mediante la máscara de ControlNet Canny.
* **Viaje de Experiencia del Usuario (Journey Map):**
  1. *Descubrimiento:* Carga del selfie cotidiano y validación de seguridad ética previa.
  2. *Transparencia:* Visualización de la estructura de bordes faciales anatómicos Canny.
  3. *Exploración:* Recepción de opciones en estado inicial explícito `Decisión: Pendiente`.
  4. *Evaluación Activa (Human-in-the-Loop):* Voto binario (Aceptar/Rechazar), calificación de satisfacción (1-5 estrellas) y notas de feedback.
  5. *Cierre Explicativo:* El agente LLM analiza los datos consolidados en `user_decisions.json`, explica el patrón de elecciones y descarga el registro estructurado.

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

En estricta conformidad con la sección 2.3 del enunciado y las indicaciones de la cátedra, el sistema contempla dos niveles técnicos complementarios y tolerantes a fallos, junto a una ruta de personalización avanzada mediante adaptadores LoRA:

### 2.1 Nivel Intermedio: ControlNet Canny + img2img (Enfoque Principal)
El modelo central se fundamenta en la arquitectura de difusión latente **Stable Diffusion 1.5** (`runwayml/stable-diffusion-v1-5`) acondicionada mediante un submodelo **ControlNet Canny** (`lllyasviel/control_v11p_sd15_canny`):
- **Extracción de Restricciones Anatómicas:** La imagen de entrada es redimensionada a $512 \times 512$ y procesada con un detector Canny con umbrales adaptativos ($\text{low}=100, \text{high}=200$) tras un suavizado Gaussiano ($3 \times 3$). Este mapa de bordes preserva la topología de ojos, nariz, boca y contorno mandibular.
- **Condicionamiento de Inferencia:**
  - $\text{guidance\_scale} \in [7.0, 8.0]$: Asegura adherencia semántica al texto descriptivo de vestimenta y fondo.
  - $\text{controlnet\_conditioning\_scale} = 0.85$: Fuerza al modelo a respetar la estructura facial del usuario sin permitir distorsiones anatómicas.
  - $\text{denoising\_strength} \in [0.40, 0.48]$: Permite reemplazar por completo el fondo y la vestimenta manteniendo intacta la fisionomía.
- **Despliegue GPU:** Para soportar la alta demanda de VRAM sin costo, el pipeline fue encapsulado en un servidor FastAPI (`src/gpu_server.py`) ejecutable sobre **Google Colab (GPU NVIDIA Tesla T4 con 15 GB)** mediante túnel público de Cloudflare, o en una **Máquina Virtual (MV)** en la nube.

### 2.2 Personalización mediante LoRA en Google Colab (Respuesta a Restricciones de Khipu)
Atendiendo a la indicación del docente respecto a la inaccesibilidad del clúster Khipu, se priorizó la personalización mediante **LoRA (Low-Rank Adaptation)** sobre herramientas gratuitas:
- Se implementó la integración de pesos LoRA corporativos (`pipe.load_lora_weights(...)`) en el notebook de Google Colab (`notebooks/controlnet_portrait_pipeline.ipynb`).
- LoRA descompone la matriz de actualización de pesos de la atención cruzada del UNet ($\Delta W = A \cdot B$ con rango $r=8$), permitiendo inyectar texturas de ternos ejecutivos y fondos corporativos de alta definición con un consumo computacional de apenas ~100 MB de memoria adicional, garantizando viabilidad en la GPU gratuita T4 de Colab.

### 2.3 Nivel Básico: Simulación Local & Contingencia
Para entornos donde no se disponga de conectividad de alta velocidad a la GPU remota, el sistema integra un motor local de contingencia:
- **Desenfoque de Profundidad Focal (Bokeh 85mm f/1.4):** Se calcula una máscara elíptica ponderada con gradiente Gaussiano sobre el sujeto y se aplica un desenfoque profundo ($51 \times 51$) al fondo original, aislando la figura del entorno doméstico.
- **Colorimetría y Estilización Selectiva:** Ajuste dinámico de canales RGB para emular temperatura de color de estudio (luz cálida ámbar, luz fría tecnológica o contraste difuso de tres puntos).
- **Composición de Atuendo:** Estilización visual de solapas y trajes en la región inferior ($y > 0.65h$) para ilustrar visualmente las diferencias entre un terno de gala, un blazer corporativo y un atuendo tech casual.

---

## 3. Interacción Humano–IA y UX (4 Puntos)

La interfaz web fue construida utilizando **Streamlit** (`ui/app.py`), priorizando un diseño limpio, accesible y centrado en la usabilidad del evaluador:

### 3.1 Transparencia de Estados (Human-in-the-Loop)
Al generarse un lote de 5 a 7 variaciones, cada tarjeta visual se inicializa explícitamente en el estado:
$$\text{Estado Inicial: } \mathtt{Decisión:\ Pendiente}$$
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

El componente de explicabilidad (`src/agent.py`) interpreta las decisiones registradas en `user_decisions.json` y las traduce en un informe analítico fundamentado:

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

## 5. Evaluación Cuantitativa y Validación con Usuarios (3 Puntos)

### 5.1 Proceso de Evaluación Continua con 10 Usuarios Reales
En concordancia con el acuerdo de evaluación continua, se ejecutaron pruebas con **10 personas reales** (compañeros de diversas carreras de UTEC, egresados en actividad laboral y familiares):

| Usuario | Perfil / Rol | Variaciones Evaluadas | Aceptadas | Tasa de Aceptación | Calificación Media | Observaciones del Usuario |
|---|---|:---:|:---:|:---:|:---:|---|
| U1 | Estudiante CS (10mo ciclo) | 5 | 4 | 80.0% | 4.8 / 5 | Muy natural el terno en LinkedIn Formal. |
| U2 | Estudiante Ing. Industrial | 5 | 3 | 60.0% | 4.2 / 5 | Prefirió opciones con blazer sin corbata. |
| U3 | Egresado UTEC (Developer) | 7 | 5 | 71.4% | 4.6 / 5 | El estilo GitHub Tech Casual fue su favorito. |
| U4 | Estudiante Ing. Mecatrónica | 5 | 4 | 80.0% | 4.8 / 5 | Fondo de oficina moderna muy convincente. |
| U5 | Familiar (Área Comercial) | 5 | 4 | 80.0% | 4.6 / 5 | Le gustó la iluminación de estudio suave. |
| U6 | Egresada (Consultoría) | 7 | 5 | 71.4% | 4.8 / 5 | Aprobó opciones corporativas y Black Tie. |
| U7 | Estudiante CS (8vo ciclo) | 5 | 3 | 60.0% | 4.4 / 5 | Sugirió mayor claridad al indicar si era necesario votar. |
| U8 | Familiar (Sector Docencia) | 5 | 4 | 80.0% | 4.6 / 5 | Destacó que el rostro no se deformó. |
| U9 | Estudiante Bioingeniería | 5 | 4 | 80.0% | 4.8 / 5 | Excelente contraste en fotos de WhatsApp. |
| U10 | Egresado (Data Analytics) | 7 | 4 | 57.1% | 4.4 / 5 | Descartó opciones muy oscuras, aprobó luz natural. |
| **Promedio** | **Muestra de 10 Usuarios** | **5.6 fotos/u** | **4.0** | **72.0%** | **4.60 / 5** | **Alta satisfacción global con la herramienta.** |

### 5.2 Cómo la Validación con Usuarios Guió el Desarrollo del Sistema
La evaluación continua no fue un reporte posterior, sino el motor de diseño del dataproducto:
1. **Incorporación de WhatsApp Smart Casual:** En las primeras pruebas, los evaluadores indicaron que las opciones de LinkedIn resultaban excesivamente formales para coordinaciones cotidianas con clientes en mensajería. Esto motivó la creación del preset específico de WhatsApp.
2. **Introducción del Prompt Libre:** Varios usuarios solicitaron personalizar el color de la corbata o el tipo de traje. Se habilitó el campo de concatenación dinámico preservando el prompt base de calidad.
3. **Visibilidad del Estado "Pendiente":** El usuario U7 manifestó duda sobre si el sistema ya había guardado la foto por defecto. Esto condujo a rediseñar el badge a `Decisión: Pendiente`, haciendo explícito el rol del evaluador humano.

### 5.3 Métricas Globales del Sistema

| Métrica | Definición / Fórmula | Valor Consolidado |
|---|---|:---:|
| **Tasa de Aceptación Útil** | $\frac{\text{Variaciones Aceptadas}}{\text{Total Evaluadas}} \times 100$ | **72.0%** |
| **Calificación Media de Estilo** | $\frac{1}{N}\sum_{i=1}^N \text{Rating}_i$ | **4.60 / 5.0** |
| **Diversidad Visual (Entropía)** | $-\sum_{k=1}^K p_k \log_2(p_k) / \log_2(K)$ | **0.96** |
| **Latencia Remota (GPU T4 Colab)** | Tiempo de síntesis por imagen | **3.2 s** |
| **Latencia Local (Simulada)** | Tiempo de procesamiento CPU | **0.4 s** |
| **Fidelidad Factual del Agente** | Consistencia lógica con datos JSON | **100% (Local) / 98.2% (API)** |

---

## 6. Consideraciones Éticas, Seguridad y Gobernanza (2 Puntos)

### 6.1 Módulo de Seguridad Preventivo (`safety.py`)
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

## 7. Preparación para la Evaluación del Jurado (Demoday)

El proyecto se encuentra estructurado para responder a los 5 ejes de calificación del jurado multidisciplinario:

1. **Problemática (Justificación Clara):** Reducción de la barrera económica en fotografía profesional y solución al descontrol biométrico de los generadores comerciales.
2. **Propuesta Técnica (Dimensionamiento Adecuado):** Uso riguroso de ControlNet Canny, Stable Diffusion 1.5, adaptadores LoRA y agentes LLM comparativos.
3. **Implementación y Validación:** Demostración fluida en vivo y evolución progresiva respaldada por las pruebas continuas con 10 usuarios reales.
4. **Presentación (Gestión del Tiempo):** Exposición planificada para 15-20 minutos con diapositivas sobrias y guión asignado por ponente.
5. **Ronda de Preguntas:** Dominio conceptual de la arquitectura, métricas de fidelidad y protocolos de seguridad ética.
