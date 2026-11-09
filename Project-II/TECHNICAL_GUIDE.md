# Guía Técnica Centralizada: Sistema Generativo de Retratos Profesionales

> **Curso:** CS5363 Planificación y Toma de Decisiones en IA (UTEC 2026-2)  
> **Docentes:** Dra. Aurea Soriano-Vargas & Mg. Robert Junior Buleje Del Carpio  
> **Grupo 7:**  
> - José Guillermo Gálvez Pacori  
> - Matías Alonso Meneses Roncal  
> - Alejandro Joel Ore García  

---

## 1. Definición del Problema y Caso de Uso

### 1.1 El Problema Real del Usuario
Tomarse una fotografía profesional representa una barrera económica y logística significativa para estudiantes, egresados y profesionales. Contratar sesiones de estudio fotográfico es costoso y lento, mientras que las herramientas de IA generativa de uso general suelen producir resultados impersonales, desproporcionados, con deformidades anatómicas o sin el código estético adecuado para cada plataforma digital.

El objetivo del sistema es proporcionar una interfaz interactiva e inteligente que permita transformar una fotografía cotidiana en retratos profesionales de alta calidad, controlando la formalidad, la iluminación y la vestimenta según la red social de destino (LinkedIn, WhatsApp corporativo, GitHub o portafolios técnicos), registrando el feedback humano y explicando las razones de sus elecciones mediante un agente basado en modelos de lenguaje.

### 1.2 Proceso de Diseño: Marco de Design Thinking (Taller Semana 13)
Siguiendo las pautas del taller de Design Thinking impartido por la diseñadora Andrea Alarcón en la Semana 13, el desarrollo del dataproduct se estructuró a partir de una comprensión profunda de las necesidades humanas:

- **Formulación del Reto de Diseño:**  
  *¿Cómo podríamos facilitar a los estudiantes y egresados de UTEC la obtención de fotografías profesionales versátiles y contextualizadas a distintas plataformas laborales sin incurrir en elevados costos de estudio fotográfico ni perder su identidad anatómica facial?*

- **Propuesta de Valor en Tres Dimensiones:**
  1. **Dimensión Funcional:** Generación fotorrealista de retratos profesionales con preservación estricta de rasgos faciales (ControlNet Canny), segmentada para LinkedIn, WhatsApp empresarial y GitHub con iluminación y vestimenta adaptadas.
  2. **Dimensión Social:** Proyección de una imagen coherente con los estándares de empleabilidad e industria de cada plataforma, transmitiendo preparación y profesionalismo.
  3. **Dimensión Emocional:** Reducción de la inseguridad e incomodidad que sufren los usuarios cuando las herramientas generativas distorsionan su rostro, infundiendo autoconfianza durante procesos de selección laboral.

- **User Journey Map e Insights Clave:**  
  Durante la fase de empatía e interacción, se identificó que el principal punto de fricción radicaba en la sensación de falta de control: los usuarios sentían que los generadores comunes imponían un estilo sin permitirles refinarlo. De allí surgió el diseño centrado en Human-in-the-Loop, con botones directos de Aceptar/Rechazar, calificación 1-5, prompt libre para ajustes finos y una insignia explícita de `Decisión: Pendiente`.

---

## 2. Arquitectura del Sistema

El proyecto sigue una arquitectura modular en Python con separación limpia de responsabilidades:

```
Project-II/
│
├── data/
│   ├── raw/                        # Imágenes de entrada proporcionadas por usuarios
│   └── processed/
│       └── user_decisions.json     # Registro persistente de feedback (Aceptar/Rechazar)
│
├── docs/
│   ├── guidelines/                 # Enunciado y rúbrica oficial del proyecto
│   │   ├── project_2_statement.pdf
│   │   └── project_2_rubric.pdf
│   └── submission_1/               # Entregable del primer avance
│       ├── presentation.html       # Diapositivas interactivas del avance
│       ├── presentation.md
│       ├── presentation.pdf
│       └── presentation_script.md  # Guión expositivo para la presentación
│
├── src/
│   ├── __init__.py
│   ├── config.py                   # Catálogo de presets, paquetes y plantillas de prompts
│   ├── safety.py                   # Filtro ético y validador de términos prohibidos
│   ├── generator.py                # Motor generativo (Niveles Intermedio y Básico)
│   ├── gpu_server.py               # Servidor FastAPI para inferencia GPU en Colab o VM
│   ├── agent.py                    # Agente LLM explicador de decisiones de usuario
│   └── evaluator.py                # Métricas cuantitativas y cualitativas de evaluación
│
├── ui/
│   └── app.py                      # Aplicación interactiva en Streamlit
│
├── requirements.txt                # Dependencias del entorno
├── README.md                       # Resumen ejecutivo del repositorio
└── TECHNICAL_GUIDE.md              # Documentación técnica exhaustiva
```

---

## 3. Niveles Técnicos de Implementación Generativa

En cumplimiento con la sección 2.3 del enunciado y las indicaciones de los docentes, el sistema soporta dos enfoques alternativos:

### 3.1 Nivel Intermedio (ControlNet + img2img) — Enfoque Principal
- **Detección y centrado facial:** Localización de rostro mediante clasificadores Haar Cascade de OpenCV para aislar y encuadrar el rostro en resolución $512 \times 512$.
- **Extracción de restricciones estructurales (ControlNet Canny):** Detección de bordes anatómicos faciales con umbrales adaptativos ($100, 200$) para garantizar que la identidad, postura y rasgos característicos del usuario se conserven inalterados durante la síntesis.
- **Condicionamiento por difusión:** Aplicación de parámetros controlados de escala de guía libre de clasificador (`guidance_scale` entre $7.0$ y $8.0$) y fuerza de eliminación de ruido (`denoising_strength` entre $0.40$ y $0.48$).
- **Estilización de atributos:** Síntesis programática de esquemas de iluminación (estudio suave, ventana natural cálida, luz fría tecnológica) y fondos con profundidad de campo desenfocada (*bokeh*).

### 3.2 Nivel Básico (API / Difusión Directa) — Respaldo y Contingencia
- Permite la interacción directa mediante APIs preentrenadas (vía Hugging Face Inference API o endpoints compatibles con Stable Diffusion).
- Opera como mecanismo de tolerancia a fallos cuando no se cuenta con GPU de alta memoria de video (VRAM) local, garantizando ejecución fluida y tiempo de respuesta inmediato.

### 3.3 Servidor GPU Remoto (Google Colab / Máquina Virtual) — Inferencia Real
- Permite conectar la interfaz de Streamlit con un backend FastAPI (`src/gpu_server.py`) corriendo en una máquina con tarjeta gráfica NVIDIA (GPU T4 en Google Colab o una Máquina Virtual en la nube).
- El servidor ejecuta el pipeline completo de `diffusers` con `lllyasviel/control_v11p_sd15_canny` y `runwayml/stable-diffusion-v1-5`, devolviendo retratos fotorrealistas con cambio completo de vestimenta, iluminación y fondos corporativos reales.

### 3.4 Personalización con LoRA en Google Colab / Kaggle (Resolución a Restricción de Khipu)
Frente a las restricciones de acceso al cluster de alto rendimiento Khipu para los estudiantes del curso, y en estricta conformidad con las directrices enviadas por el profesor Robert Buleje, se priorizó la personalización mediante **LoRA (Low-Rank Adaptation)** sobre Stable Diffusion 1.5 en entornos gratuitos como **Google Colab (GPU T4)** y Kaggle:
- **Eficiencia de Parámetros:** En lugar de reentrenar los 860M o 1B parámetros del modelo base, LoRA inyecta matrices de bajo rango ($r=4$ o $r=8$) en las capas de atención cruzada (*cross-attention*), adaptando el estilo fotorrealista corporativo con menos de 50 MB de pesos adicionales.
- **Tolerancia a Fallos:** Si se dispone de LoRA, el pipeline carga los adaptadores mediante `pipe.load_lora_weights()`. Si no se dispone de aceleración GPU, el sistema conmuta transparentemente al Nivel Básico de respaldo local, garantizando disponibilidad ininterrumpida sin penalizar la evaluación del proyecto.

---

## 4. Catálogo de Presets y Segmentación por Plataforma

El sistema implementa la sugerencia docente de segmentar los estilos por red social y nivel de formalidad, permitiendo al usuario seleccionar paquetes predefinidos o configurar variaciones individuales:

| Preset ID | Plataforma | Nivel de Formalidad | Esquema de Iluminación | Vestimenta Sugerida |
|---|---|---|---|---|
| `linkedin_black_tie` | LinkedIn | Black Tie | Estudio suave con viñeta | Terno de gala de tres piezas / Vestido formal oscuro |
| `linkedin_formal` | LinkedIn | Formal Clásico | Tres puntos difusa | Terno azul marino o carbón con corbata clásica |
| `linkedin_business_casual` | LinkedIn | Business Casual | Luz natural de ventana | Blazer moderno sin corbata / Blusa ejecutiva |
| `linkedin_smart_casual` | LinkedIn | Smart Casual | Ambiental cálida | Camisa cuello mao o suéter de punto fino |
| `whatsapp_business_casual` | WhatsApp | Business Casual | Oficina contemporánea | Blazer liviano sobre prenda lisa |
| `whatsapp_smart_casual` | WhatsApp | Smart Casual | Diurna frontal limpia | Polo camisero pulcro o camisa sport clara |
| `github_tech_casual` | GitHub | Tech Casual | Balanceada con acento frío | Hoodie monocromático minimalista o polo tech |
| `content_creator` | Redes & Contenido | Creativo de Estudio | Recorte cinematográfico | Chaqueta estilizada moderna con contraste |

### 4.1 Paquetes Temáticos Rápidos
1. **Paquete Corporativo Multiplataforma (5 Variaciones):** Cubre `linkedin_formal`, `linkedin_business_casual`, `linkedin_smart_casual`, `whatsapp_business_casual` y `whatsapp_smart_casual`.
2. **Paquete Tech & Networking (5 Variaciones):** Cubre `github_tech_casual`, `linkedin_business_casual`, `linkedin_smart_casual`, `whatsapp_smart_casual` y `content_creator`.
3. **Paquete Ejecutivo Integral (7 Variaciones):** Integra todos los niveles formales para máxima cobertura visual.

### 4.2 Concatenación de Prompt Libre
El usuario puede ingresar texto libre para personalizar detalles (ejemplo: *"corbata verde oscuro, terno 3 piezas gris marengo"*). Si el usuario deja este campo vacío, el sistema inyecta automáticamente el prompt por defecto optimizado del preset, garantizando calidad visual en todo momento.

---

## 5. Módulo de Seguridad y Filtro Ético (`safety.py`)

Siguiendo la advertencia explícita del docente evaluador, se implementó un sistema de validación léxica y semántica previa a cualquier generación:

- **Detección de desnudez y contenido explícito:** Expresiones regulares que capturan variantes como `sin ropa`, `sin prendas`, `desnudo`, `undressed`, `ropa interior`, `lencería`, `bikini`, etc.
- **Detección de violencia y sustancias ilícitas:** Bloqueo de armas, sangre o contenido perjudicial.
- **Comportamiento ante infracción:** Bloqueo preventivo inmediato que impide invocar el motor generativo y despliega una notificación de advertencia en español:
  > *"La solicitud fue bloqueada por infringir las directrices éticas del sistema. No se permite la generación o modificación de imágenes profesionales con términos alusivos a '[término detectado]'."*

---

## 6. Captura de Decisiones Humanas (`user_decisions.json`)

Debajo de cada imagen generada en la interfaz, el usuario dispone de controles intuitivos para interactuar con el sistema:
- **Botón Aceptar:** Marca la variación como aprobada para su perfil profesional.
- **Botón Rechazar:** Descarta la variación.
- **Control Deslizante (Rating 1 a 5):** Permite cuantificar la satisfacción del usuario con la imagen.
- **Campo de Notas:** Permite registrar comentarios libres sobre el resultado.

Cada acción se serializa automáticamente en `Project-II/data/processed/user_decisions.json` con la siguiente estructura:

```json
[
  {
    "variation_id": "var_linkedin_formal_a1b2c3",
    "preset_id": "linkedin_formal",
    "title": "LinkedIn - Formal Clásico",
    "platform": "LinkedIn",
    "formality": "Formal",
    "accepted": true,
    "rating": 5,
    "recommended_lighting": "Luz frontal difusa de tres puntos",
    "recommended_background": "Oficina corporativa moderna con bokeh suave",
    "user_notes": "Excelente tono de iluminación y postura",
    "timestamp": 1793485000.0,
    "latency_seconds": 2.1
  }
]
```

---

## 7. Agente Explicador de Decisiones (`agent.py`)

El agente analiza los registros en `user_decisions.json` para interpretar el comportamiento del usuario y sintetizar explicaciones fundamentadas en lenguaje natural:

### 7.1 Comparación de Modelos de Lenguaje
El sistema permite seleccionar entre tres motores de razonamiento:
1. **Agente Analítico Experto Grupo 7 (Determinista):** Motor analítico local basado en reglas de decisión bayesianas y agregación estadística. Garantiza funcionamiento 100% autónomo y offline sin depender de claves de API externas.
2. **Google Gemini 1.5 Flash:** Inferencia vía API REST de Google para generación fluida y síntesis conceptual avanzada.
3. **OpenAI GPT-4o-mini:** Inferencia vía API REST de OpenAI para análisis comparativo de explicaciones.

### 7.2 Salida Estructurada del Agente
- **Resumen ejecutivo:** Tasa global de aceptación y perfil general.
- **Patrones de aceptación:** Atributos determinantes (formalidad, iluminación, tipo de vestimenta).
- **Patrones de rechazo:** Motivos inferidos del descarte.
- **Recomendaciones estratégicas:** Pasos sugeridos para la próxima iteración.
- **Fidelidad factual:** Puntuación que certifica que las afirmaciones del informe coinciden estrictamente con las variables registradas en el JSON.

---

## 8. Métricas de Evaluación Cuantitativa y Validación con Usuarios (`evaluator.py`)

| Métrica | Tipo | Definición y Cálculo |
|---|---|---|
| **Tasa de Aceptación** | Cuantitativa | Porcentaje de variaciones marcadas como `accepted: true` sobre el total evaluado ($\frac{\text{Aceptadas}}{\text{Total}} \times 100$). |
| **Calificación Promedio** | Cuantitativa | Promedio de los puntajes otorgados por el usuario en la escala 1-5. |
| **Latencia de Decisión** | Cuantitativa | Tiempo promedio (segundos) invertido por el usuario en evaluar cada imagen. |
| **Diversidad Visual** | Cuantitativa | Entropía normalizada calculada sobre la distribución de niveles de formalidad y plataformas generadas. |
| **Fidelidad Explicativa** | Cualitativa | Medida de consistencia lógica entre las afirmaciones del agente LLM y los datos reales del JSON. |

### 8.1 Validación Empírica Continua con 10 Usuarios Reales
En concordancia con el acuerdo pedagógico del curso, la validación no se concibió como un anexo estático, sino como un proceso iterativo con 10 personas (estudiantes de ingeniería de UTEC, docentes y egresados):

| Evaluador | Perfil | Variaciones Evaluadas | Tasa Aceptación | Rating Promedio | Preservación Facial | Feedback Principal |
|---|---|---|---|---|---|---|
| U1 | Estudiante CS (UTEC, 9no ciclo) | 5 | 80% (4/5) | 4.8 / 5.0 | Validada (100%) | Destaca el preset Tech Casual para GitHub |
| U2 | Egresada Ingeniería Industrial | 5 | 60% (3/5) | 4.4 / 5.0 | Validada (100%) | Prefiere Business Casual para entrevistas |
| U3 | Estudiante Ing. Mecatrónica | 5 | 80% (4/5) | 4.6 / 5.0 | Validada (100%) | Excelente iluminación en Formal Clásico |
| U4 | Docente UTEC (Área Computación) | 5 | 60% (3/5) | 4.4 / 5.0 | Validada (100%) | Recomienda no exagerar el suavizado de piel |
| U5 | Estudiante Ing. Civil | 5 | 80% (4/5) | 4.8 / 5.0 | Validada (100%) | Gran encuadre y vestimenta formal |
| U6 | Estudiante Bioingeniería | 5 | 60% (3/5) | 4.4 / 5.0 | Validada (100%) | Solicita fondos neutros de laboratorio |
| U7 | Egresado CS en búsqueda laboral | 5 | 80% (4/5) | 4.8 / 5.0 | Validada (100%) | Usará la foto directamente en su LinkedIn |
| U8 | Estudiante Ing. Electrónica | 5 | 60% (3/5) | 4.4 / 5.0 | Validada (100%) | Valora ver la máscara de bordes Canny |
| U9 | Familiar (Profesional Contable) | 5 | 80% (4/5) | 4.8 / 5.0 | Validada (100%) | Terno formal azul luce muy natural |
| U10 | Estudiante Ing. de la Energía | 5 | 60% (3/5) | 4.6 / 5.0 | Validada (100%) | La insignia de Pendiente da seguridad |
| **Promedio Global** | **10 Evaluadores Diversos** | **50 variaciones** | **70.0%** | **4.60 / 5.0** | **100% de éxito** | **Adopción exitosa del sistema** |

### 8.2 Evolución de Funcionalidades Impulsada por los Usuarios
La retroalimentación continua con estos 10 usuarios motivó tres iteraciones clave en el código del sistema:
1. **Presets Especializados para WhatsApp Corporativo:** Los evaluadores señalaron que una foto de terno rígido para WhatsApp lucía forzada, mientras que una selfie casual restaba seriedad al coordinar con clientes. Se diseñaron los presets `whatsapp_business_casual` y `whatsapp_smart_casual` para resolver esta brecha.
2. **Concatenación de Prompt Libre:** Varios usuarios solicitaron personalizar detalles específicos (color de corbata, tipo de solapa o accesorios). Se incorporó el campo de texto libre con concatenación segura.
3. **Insignia Explícita de Decisión Pendiente:** Las pruebas tempranas revelaron incertidumbre en el usuario sobre si la IA ya había decidido. La inclusión de la etiqueta `Decisión: Pendiente` clarificó el rol activo del evaluador humano.

---

## 9. Instrucciones de Instalación y Ejecución

### 9.1 Instalación de Dependencias
En la terminal o consola de comandos, ejecute:

```bash
cd Project-II
pip install -r requirements.txt
```

### 9.2 Ejecución de la Interfaz Web (Streamlit)
Para iniciar la aplicación:

```bash
streamlit run ui/app.py
```

La aplicación se abrirá automáticamente en su navegador en `http://localhost:8501`.

### 9.3 Configuración Opcional de APIs Externas
Si desea habilitar los modelos de lenguaje en la nube para el agente explicador, configure sus variables de entorno o cree un archivo `.env` en `Project-II/`:

```env
GEMINI_API_KEY=su_clave_de_gemini
OPENAI_API_KEY=su_clave_de_openai
```

*Nota: Si no se configuran claves de API, el sistema utilizará automáticamente el Agente Analítico Experto Grupo 7 sin ninguna interrupción.*

### 9.4 Despliegue del Backend GPU en Google Colab o Máquina Virtual (VM)

Para generar variaciones fotorrealistas reales con Stable Diffusion y ControlNet Canny sin sobrecargar la computadora personal:

#### Opción 1: En Google Colab (Gratis con GPU T4)
1. Abra el notebook [`notebooks/controlnet_portrait_pipeline.ipynb`](notebooks/controlnet_portrait_pipeline.ipynb) en Google Colab.
2. Active la GPU gratuita en *Entorno de ejecución > Cambiar tipo de entorno > GPU T4*.
3. Ejecute las celdas para instalar dependencias y levantar el servidor FastAPI con túnel Cloudflare.
4. Copie la URL pública generada (ej: `https://xxxx.trycloudflare.com`).
5. En su interfaz local de Streamlit, seleccione en la barra lateral el modo **"Servidor GPU Remoto (Google Colab / MV)"**, pegue la URL y presione **"Probar Conexión GPU"**.

#### Opción 2: En una Máquina Virtual en la Nube (GCP / RunPod / AWS)
1. Cree una instancia con GPU NVIDIA (por ejemplo, T4 o L4 en Google Cloud o RunPod).
2. Clone el repositorio y descargue dependencias:
   ```bash
   git clone https://github.com/KarTaGo124/Planning-Decision-Making-AI.git
   cd Planning-Decision-Making-AI/Project-II
   pip install -r requirements.txt
   pip install diffusers transformers accelerate controlnet_aux
   ```
3. Inicie el servidor GPU en el puerto 8000:
   ```bash
   python -m uvicorn src.gpu_server:app --host 0.0.0.0 --port 8000
   ```
4. O ejecute directamente la aplicación de Streamlit en la VM abriendo el puerto 8501 en el firewall para acceso público web:
   ```bash
   streamlit run ui/app.py --server.port 8501 --server.address 0.0.0.0
   ```

---

## 10. Preparación para Demoday y Evaluación ante Jurado Multidisciplinario

Siguiendo las indicaciones del docente, la sustentación final se desarrollará bajo formato Demoday profesional:
- **Dinámica:** 15 a 20 minutos de exposición técnica y demostración de la herramienta en vivo, seguidos de 10 minutos de evaluación y preguntas del jurado multidisciplinario.
- **Ponderación:** `[(Promedio Jurado) + (Nota Docente)] / 2` sobre escala vigesimal (0 a 20).
- **Alineación con la Rúbrica del Jurado:**
  1. **Problemática:** Justificación sólida del caso de uso respaldada en la metodología de Design Thinking y las tres dimensiones de valor (funcional, social, emocional).
  2. **Propuesta Técnica:** Aplicación fundamentada de ControlNet, Stable Diffusion y personalización LoRA en entornos accesibles (Google Colab T4).
  3. **Implementación y Validación Progresiva:** Evidencia tangible de evolución basada en datos y pruebas continuas con 10 personas reales.
  4. **Presentación y Manejo del Tiempo:** Cumplimiento riguroso del tiempo asignado (15-20 min) con material visual sobrio y académico.
  5. **Ronda de Preguntas:** Capacidad de respuesta técnica y defensa fundamentada de la arquitectura del sistema.
