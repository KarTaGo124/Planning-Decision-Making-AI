# Proyecto 2: Sistema Generativo Interactivo para Variaciones Visuales con Feedback Humano y Explicación mediante Agentes de IA

**Curso:** CS5363 Planificación y Toma de Decisiones en IA — UTEC (2026-2)  
**Profesores:** Dra. Aurea Soriano-Vargas & Mg. Robert Junior Buleje Del Carpio  
**Grupo 7:**  
- José Guillermo Gálvez Pacori  
- Matías Alonso Meneses Roncal  
- Alejandro Joel Ore García  

---

## Slide 1: Portada y Presentación del Proyecto
* **Título Oficial:** Sistema Generativo Interactivo para Variaciones Visuales con Feedback Humano y Explicación mediante Agentes de IA.
* **Caso de Uso:** Asistente Interactivo de Retratos Profesionales Multiplataforma (LinkedIn, WhatsApp Corporativo, GitHub).
* **Nivel Técnico:** Nivel Intermedio (ControlNet Canny + *img2img* + LoRA en Colab + Agente Explicador LLM + Interfaz Streamlit).
* **Equipo:** Grupo 7 (Gálvez Pacori, Meneses Roncal, Ore García).

---

## Slide 2: Problema Real y Proceso de Design Thinking (Semana 13)
* **El Reto Centrado en las Personas (Andrea Alarcón):**  
  *¿Cómo podríamos facilitar la generación accesible, contextualizada y controlada de retratos para estudiantes de UTEC?*
* **Propuesta de Valor en Tres Dimensiones:**
  - *Funcional:* Presets preconfigurados por plataforma digital y personalización mediante *prompt libre*.
  - *Social:* Imagen creíble y profesional para reclutadores en LinkedIn y clientes en WhatsApp corporativo.
  - *Emocional:* Tranquilidad al comprobar que sus rasgos biométricos reales no se deforman.
* **Viaje del Usuario (Journey Map):**  
  Selfie cotidiano -> Visualización de bordes Canny -> Generación de 5-7 variaciones -> Votación Human-in-the-Loop -> Informe analítico del agente LLM.

---

## Slide 3: Arquitectura General del Sistema
* **Paso 1: Entrada y Validación Ética (`safety.py`):** Carga del retrato y comprobación contra términos prohibidos (desnudez, violencia, no profesional).
* **Paso 2: Preprocesamiento y Extracción Estructural (`generator.py`):** Centrado facial con OpenCV Haar Cascade y extracción de bordes anatómicos faciales con ControlNet Canny.
* **Paso 3: Síntesis Generativa Multi-Nivel:** Inferencia en GPU remota con Stable Diffusion 1.5 + ControlNet Canny + LoRA o motor de contingencia local.
* **Paso 4: Feedback Humano y Registro:** Evaluación en Streamlit con botones Aceptar/Rechazar, calificación 1-5 y guardado en `user_decisions.json`.
* **Paso 5: Agente Explicador LLM (`agent.py`):** Síntesis analítica de patrones de aceptación/descarte con fidelidad factual certificada.

---

## Slide 4: Motores Generativos (ControlNet & Personalización LoRA)
* **Nivel Intermedio (Enfoque Principal - ControlNet Canny):**
  - Condicionamiento geométrico que fija la posición de ojos, nariz, boca y contorno mandibular.
  - Parámetros: `guidance_scale` (7.0 - 8.0) y `denoising_strength` (0.40 - 0.48).
  - Permite transformar vestimenta y fondo sin alterar la identidad del sujeto.
  - *Personalización LoRA en Google Colab:* Adaptadores de bajo rango para texturas ejecutivas ante restricciones de Khipu.
* **Nivel Básico (Enfoque de Respaldo / Contingencia):**
  - Simulación local de profundidad de campo (desenfoque bokeh con lente equivalente 85mm f/1.4).
  - Balance de blancos, colorimetría corporativa y estilización de solapa.
  - Garantiza que la aplicación funcione en cualquier laptop sin requerir GPU local (0.4 s de respuesta).

---

## Slide 5: Catálogo de Presets y Segmentación de Plataformas
* **LinkedIn:**
  - *Black Tie:* Terno de gala o vestido formal oscuro con viñeta sutil de estudio.
  - *Formal Clásico:* Terno azul marino/carbón, corbata y luz difusa de tres puntos.
  - *Business Casual:* Blazer moderno sin corbata, luz natural de ventana.
  - *Smart Casual:* Suéter o camisa sport elegante para sectores tecnológicos.
* **WhatsApp:**
  - *Business Casual:* Presencia ágil para mensajería empresarial con clientes.
  - *Smart Casual:* Retrato cercano, luminoso y accesible con polo camisero.
* **GitHub / Portafolio:**
  - *Tech Casual:* Hoodie minimalista o polo tech con tenue iluminación fría de acento.
* **Personalización:** Paquetes temáticos rápidos (5-7 variaciones) y campo de *prompt libre* para detalles específicos de vestimenta.

---

## Slide 6: Módulo de Seguridad y Filtro Ético
* **Filtro Preventivo Estricto (`safety.py`):**
  - Expresiones regulares que capturan términos como `sin ropa`, `sin prendas`, `desnudo`, `undressed`, `ropa interior`, `lencería`, `bikini`, etc.
  - Detección de armas, sustancias ilícitas o violencia.
  - Normalización Unicode NFKD para prevenir evasiones por tildes o caracteres especiales.
* **Comportamiento ante Infracción:**
  - Bloqueo instantáneo de la inferencia.
  - Notificación formal en pantalla: *"La solicitud fue bloqueada por infringir las directrices éticas del sistema (Categoría: Desnudez). No se permite la generación o modificación de imágenes profesionales con términos alusivos a 'sin ropa'."*

---

## Slide 7: Interfaz Gráfica Human-in-the-Loop (`ui/app.py`)
* **Estado Claro de Decisión:**
  - Las fotos inician con la etiqueta `Decisión: Pendiente`, indicando que requieren revisión.
  - Al votar, cambian en vivo a `Decisión: Aceptada` o `Decisión: Rechazada`.
* **Captura Estructurada:**
  - Slider de calificación de estilo (1 a 5 estrellas).
  - Caja de texto para observaciones cualitativas.
  - Serialización automática en `data/processed/user_decisions.json`.
  - Botón de descarga directa del dataset de decisiones en formato JSON.

---

## Slide 8: Agente Explicador de Decisiones (LLM)
* **Comparativa Multimodelo:**
  1. *Agente Analítico Grupo 7 (Experto Determinista):* Reglas heurísticas y agregación estadística bayesiana, 100% offline y autónomo.
  2. *Google Gemini 1.5 Flash:* Razonamiento conceptual y redacción ejecutiva fluida.
  3. *OpenAI GPT-4o-mini:* Síntesis analítica comparativa.
* **Contenido del Informe:**
  - Tasa de aprobación global.
  - Factores determinantes en fotos aceptadas (formalidad, esquema de luz).
  - Razones de descarte en fotos rechazadas.
  - Recomendaciones para la próxima generación.
  - Puntuación de fidelidad factual contra el archivo JSON (100% en local / 98.2% en API).

---

## Slide 9: Evaluación Continua y Validación con 10 Usuarios
* **Proceso Empírico de Validación Continua:**
  - Pruebas con 10 personas reales (compañeros de UTEC de diversas carreras, egresados y familiares).
  - Tasa de Aceptación Útil: **72.0%** en la muestra experimental.
  - Calificación Media de Estilo: **4.60 / 5.0**.
  - Diversidad Visual: **0.96** (alta entropía en cobertura de estilos y plataformas).
* **Cómo los 10 Usuarios Guiaron las Iteraciones:**
  - Creación del preset de WhatsApp para cercanía cotidiana ante feedback de usuarios comerciales.
  - Incorporación del campo de prompt libre ante la solicitud de personalizar color de corbata.
  - Rediseño del badge a `Decisión: Pendiente` para aclarar la necesidad de voto humano.

---

## Slide 10: Conclusiones, Despliegue y Preparación Demoday
* **Despliegue Híbrido:**
  1. *Google Colab (Gratuito con GPU T4):* Mediante `notebooks/controlnet_portrait_pipeline.ipynb` con túnel Cloudflare público hacia Streamlit.
  2. *Máquina Virtual en la Nube (GCP / RunPod):* Ejecución con `src/gpu_server.py` o interfaz web abierta en puerto 8501.
  3. *Ejecución Local Rápida:* Ejecución con `run_app.bat` para presentaciones sin conexión a internet.
* **Preparación para el Jurado Multidisciplinario (Demoday):**
  - Problemática adecuadamente motivada con Design Thinking.
  - Propuesta técnica rigurosa (ControlNet + LoRA + LLM).
  - Implementación sustentada en 10 usuarios y demostración fluida en vivo.
  - Gestión óptima del tiempo (15-20 min) y solvencia técnica en preguntas.
