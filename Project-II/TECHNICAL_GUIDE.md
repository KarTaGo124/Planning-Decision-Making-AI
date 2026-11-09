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

## 8. Métricas de Evaluación Cuantitativa y Cualitativa (`evaluator.py`)

| Métrica | Tipo | Definición y Cálculo |
|---|---|---|
| **Tasa de Aceptación** | Cuantitativa | Porcentaje de variaciones marcadas como `accepted: true` sobre el total evaluado ($\frac{\text{Aceptadas}}{\text{Total}} \times 100$). |
| **Calificación Promedio** | Cuantitativa | Promedio de los puntajes otorgados por el usuario en la escala 1-5. |
| **Latencia de Decisión** | Cuantitativa | Tiempo promedio (segundos) invertido por el usuario en evaluar cada imagen. |
| **Diversidad Visual** | Cuantitativa | Entropía normalizada calculada sobre la distribución de niveles de formalidad y plataformas generadas. |
| **Fidelidad Explicativa** | Cualitativa | Medida de consistencia lógica entre las afirmaciones del agente LLM y los datos reales del JSON. |

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
5. En su interfaz local de Streamlit, seleccione en la barra lateral el modo **"Servidor GPU Remoto (Google Colab / MV)"**, pegue la URL y presione **"🔌 Probar Conexión GPU"**.

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
