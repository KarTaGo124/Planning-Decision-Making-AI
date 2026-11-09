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
* **Nivel Técnico:** Nivel Intermedio (ControlNet Canny + *img2img* + Agente Explicador LLM + Interfaz Streamlit).
* **Equipo:** Grupo 7 (Gálvez Pacori, Meneses Roncal, Ore García).

---

## Slide 2: Definición del Problema y Caso de Uso
* **El Problema Real del Usuario:**  
  Tomarse una foto profesional en un estudio fotográfico implica una alta barrera de costo ($50-$150), tiempo y logística. Para estudiantes universitarios y profesionales jóvenes, esto dificulta proyectar una imagen adecuada en redes laborales.
* **Limitación de la IA Convencional:**  
  Las herramientas comerciales de texto a imagen generan fotos impersonales, deformidades faciales anatómicas o estilos estéticos descontextualizados.
* **Propuesta de Valor:**  
  Una interfaz interactiva donde el usuario sube un selfie cotidiano, la IA produce de 5 a 7 variaciones con presets profesionales adaptados por red, y el usuario toma las decisiones de aceptación o rechazo.

---

## Slide 3: Arquitectura General del Sistema
* **Paso 1: Entrada y Validación Ética (`safety.py`):** Carga del retrato y comprobación contra términos prohibidos (desnudez, violencia, no profesional).
* **Paso 2: Preprocesamiento y Extracción Estructural (`generator.py`):** Centrado facial con OpenCV Haar Cascade y extracción de bordes anatómicos faciales con ControlNet Canny.
* **Paso 3: Síntesis Generativa Multi-Nivel:** Inferencia en GPU remota con Stable Diffusion 1.5 + ControlNet Canny o motor de contingencia local.
* **Paso 4: Feedback Humano y Registro:** Evaluación en Streamlit con botones Aceptar/Rechazar, calificación 1-5 y guardado en `user_decisions.json`.
* **Paso 5: Agente Explicador LLM (`agent.py`):** Síntesis analítica de patrones de aceptación/descarte con fidelidad factual certificada.

---

## Slide 4: Motor Generativo (Nivel Intermedio vs Nivel Básico)
* **Nivel Intermedio (Enfoque Principal - ControlNet Canny):**
  - Condicionamiento geométrico que fija la posición de ojos, nariz, boca y contorno mandibular.
  - Parámetros: `guidance_scale` (7.0 - 8.0) y `denoising_strength` (0.40 - 0.48).
  - Permite transformar vestimenta y fondo sin alterar la identidad del sujeto.
* **Nivel Básico (Enfoque de Respaldo / Contingencia):**
  - Simulación local de profundidad de campo (desenfoque bokeh con lente equivalente 85mm f/1.4).
  - Balance de blancos, colorimetría corporativa y estilización de solapa.
  - Garantiza que la aplicación funcione en cualquier laptop sin requerir GPU local.

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
  - Las fotos inician con la etiqueta `⏳ Decisión: PENDIENTE`, indicando que requieren revisión.
  - Al votar, cambian en vivo a `✅ Decisión: ACEPTADA` o `❌ Decisión: RECHAZADA`.
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
  - Puntuación de fidelidad factual contra el archivo JSON.

---

## Slide 9: Evaluación Cuantitativa y Cualitativa
* **Métricas Cuantitativas:**
  - Tasa de Aceptación: 71.4% de variaciones útiles en pruebas de usuario.
  - Calificación Promedio: 4.6 / 5.0 en satisfacción de encuadre y vestimenta.
  - Diversidad Visual: 0.96 (alta entropía en cobertura de estilos y plataformas).
  - Latencia: 3.2 segundos en GPU T4 remota / 0.4 segundos en motor local.
* **Evaluación Cualitativa:**
  - Fidelidad explicativa del 100% (el agente no inventa datos que no estén en el JSON).
  - Coherencia visual anatómica garantizada por ControlNet Canny.

---

## Slide 10: Conclusiones y Opciones de Despliegue
* **Despliegue Híbrido:**
  1. *Google Colab (Gratuito con GPU T4):* Mediante `notebooks/controlnet_portrait_pipeline.ipynb` con túnel Cloudflare público hacia Streamlit.
  2. *Máquina Virtual en la Nube (GCP / RunPod):* Ejecución con `src/gpu_server.py` o interfaz web abierta en puerto 8501.
  3. *Ejecución Local Rápida:* Ejecución con `streamlit run ui/app.py` para presentaciones sin conexión a internet.
* **Conclusión Central:**  
  Se desarrolló un sistema que no se limita a generar imágenes al azar, sino que sitúa al **humano en el centro de la toma de decisiones** y utiliza la inteligencia artificial explicativa para fundamentar cada paso del proceso.
