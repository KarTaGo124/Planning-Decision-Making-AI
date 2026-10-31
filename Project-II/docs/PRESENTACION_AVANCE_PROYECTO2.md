# Avance Proyecto 2: Sistema Generativo Interactivo con Feedback Humano y Explicación mediante Agentes de IA

**Curso:** Planificación y Toma de Decisiones en IA (CS5363) — UTEC (2026-2)  
**Profesores:** Dra. Aurea Soriano-Vargas & Mg. Robert Buleje  
**Grupo 7:** Gálvez Pacori, José Guillermo | Meneses Roncal, Matías Alonso | Ore García, Alejandro Joel  
**Caso de Uso:** Asistente Interactivo de Edición y Estilizado de Retratos Profesionales  
**Nivel Técnico:** Nivel Intermedio (Stable Diffusion con img2img / ControlNet + Agente LLM)

---

## 1. Contextualización y Planteamiento del Problema

Los avances recientes en inteligencia artificial generativa han permitido sintetizar contenido visual con un realismo fotográfico sin precedentes. No obstante, en tareas aplicadas como la fotografía corporativa, la edición de perfiles profesionales y la comunicación visual, los sistemas generativos completamente automatizados presentan una limitación fundamental: **carecen de alineación con el criterio personal, el contexto institucional y las preferencias estéticas del usuario**.

A diferencia de los problemas clásicos de predicción estática, la generación visual requiere la integración activa del ser humano en el ciclo de decisión (**Human-in-the-Loop**). Mientras el modelo generativo explora eficientemente un amplio espacio de alternativas visuales, el usuario aporta el juicio contextual indispensable para validar o descartar resultados.

Por estos motivos, se propone el desarrollo de un **sistema generativo interactivo para retratos profesionales**, donde a partir de una fotografía provista por el usuario, el sistema genera de forma controlada **exactamente cinco variaciones visuales** (variando iluminación, expresión, fondo, vestimenta y estilo editorial), permite al usuario registrar estructuradamente su aceptación o rechazo mediante una interfaz gráfica, y utiliza un **agente basado en modelos de lenguaje (LLM)** para sintetizar y justificar coherentemente el proceso de selección en lenguaje natural.

---

## 2. Definición de Objetivos

### Objetivo General
Implementar un sistema generativo interactivo para la producción controlada de variaciones visuales en retratos fotográficos, integrando retroalimentación humana explícita a través de una interfaz gráfica y explicación automatizada de decisiones mediante un agente basado en modelos de lenguaje.

### Objetivos Específicos (Secuenciales)
1. **Preparación y Caracterización de Datos:** Establecer y preprocesar el conjunto de datos de referencia (CelebA-HQ y retratos fotográficos controlados), definiendo normalizaciones, alineación facial y parámetros de acondicionamiento de atributos.
2. **Implementación Generativa Controlable:** Desarrollar el módulo generativo de nivel intermedio empleando modelos de difusión latente controlable (Stable Diffusion con img2img y ControlNet) para sintetizar cinco variaciones visuales consistentes preservando la identidad facial del sujeto.
3. **Desarrollo de la Interfaz y Registro de Decisiones:** Construir una interfaz gráfica accesible que visualice paralelamente las opciones y almacene de manera estructurada las decisiones binarias (Aceptar / Rechazar) del usuario.
4. **Integración del Agente Explicativo:** Implementar un agente basado en modelos de lenguaje (LLM) que interprete el registro de decisiones y elabore un resumen explicativo coherente, transparente y fiel al proceso de selección del usuario.
5. **Evaluación Multicriterio:** Evaluar el sistema integralmente mediante métricas de calidad y diversidad visual, coherencia lógica de las explicaciones y usabilidad de la interacción.

---

## 3. Definición de Restricciones del Sistema

1. **Preservación de Identidad Facial:** Las variaciones generadas deben limitarse a modificar los atributos contextuales (iluminación, vestimenta, fondo o estilo) sin alterar la geometría biométrica esencial del rostro, asegurando que el sujeto permanezca plenamente reconocible.
2. **Latencia Operacional y Recursos de Cómputo:** El tiempo total de síntesis para las cinco opciones no debe exceder los 30 segundos bajo entornos acelerados por GPU, respetando los límites de memoria VRAM disponibles (evitando saturación de memoria en ejecuciones locales o servidores interactivos).
3. **Consistencia Estructurada de Retroalimentación:** La captura de decisiones debe ser determinística y almacenarse en esquemas normalizados (JSON) que garanticen que el agente de lenguaje cuente con datos no ambiguos sobre qué opciones fueron aceptadas y cuáles rechazadas.

---

## 4. Métricas de Éxito

El sistema se evaluará bajo tres familias complementarias de métricas:

### A. Métricas Técnicas (Generación Visual)
* **Calidad Semántica y Alineación:** Medición mediante **CLIP-Score** para evaluar la correspondencia entre los atributos textuales/condicionales deseados y la imagen sintetizada.
* **Diversidad entre Opciones:** Evaluación mediante la distancia de características profundas (**LPIPS**) o distancia coseno entre incrustaciones de las cinco variantes generadas, verificando que las alternativas no sean idénticas o redundantes.
* **Latencia de Síntesis:** Medición del tiempo en segundos por lote de cinco imágenes.

### B. Métricas de Interacción y Decisión
* **Tasa de Aceptación Útil ($TA$):** Proporción de variaciones aceptadas por el usuario en cada sesión de evaluación:
  $$TA = \frac{\text{Variaciones Aceptadas}}{5}$$
* **Tiempo de Evaluación por Decisión:** Duración media requerida por el usuario para inspeccionar las cinco imágenes y registrar su veredicto.

### C. Métricas de Explicabilidad y Usabilidad
* **Fidelidad y Coherencia del Agente:** Precisión factual estricta (100% de coherencia verificada entre las opciones marcadas en el registro JSON y las afirmaciones explícitas en el resumen en prosa emitido por el LLM).
* **Usabilidad de la Interfaz:** Evaluación de usabilidad mediante cuestionario simplificado tipo SUS (System Usability Scale) orientado a la claridad visual y facilidad de operación.

---

## 5. Modelos Mapeados y Arquitectura del Sistema

### Módulo Generativo (Nivel Intermedio)
* **Stable Diffusion (img2img) + ControlNet (OpenPose / Canny / Depth):**
  * Permite tomar la imagen del usuario como base estructural y generar cinco variantes controladas:
    1. *Variación 1:* Iluminación de estudio fotográfico profesional.
    2. *Variación 2:* Expresión facial optimizada (sonrisa corporativa sutil).
    3. *Variación 3:* Cambio de fondo contextual (oficina ejecutiva moderna / neutro difuminado).
    4. *Variación 4:* Vestimenta formal / ejecutiva.
    5. *Variación 5:* Renderizado estético / estilo editorial.

### Agente de Lenguaje y Explicabilidad
* **Modelo LLM Instruccional:** Conexión con un modelo de lenguaje vía API estructurada con plantilla de sistema orientada a la síntesis factual de preferencias.
* **Entrada del Agente:** JSON estructurado con metadatos de los prompts condicionales y el estado binario asignado por el usuario (`accepted: true/false`).
* **Salida del Agente:** Reporte ejecutivo que expone el resumen de decisiones, justificando las elecciones según el balance estético y profesional manifestado.

---

## 6. Consideraciones Éticas y Uso Responsable

* **Privacidad de Imágenes:** Procesamiento en memoria de las fotografías de los usuarios, garantizando que ninguna imagen personal sea retenida, almacenada en bases públicas o reutilizada para reentrenar modelos sin consentimiento expreso.
* **Mitigación de Sesgos Algorítmicos:** Supervisión continua del comportamiento del modelo generativo frente a atributos demográficos protegidos (tono de piel, género y edad), evitando que los acondicionamientos de "profesionalismo" o "estudio" impongan cánones eurocéntricos o discriminatorios.
* **Prevención de Suplantación y Deepfakes:** El sistema restringe su alcance a la optimización contextual y estética de la propia imagen aportada, impidiendo la síntesis de contenido difamatorio o de suplantación malintencionada.

---

## 7. Mini Plan de Trabajo

* **Fase 1 (Etapa Inicial):** Formulación del problema, definición de objetivos, restricciones operativas, métricas y diseño de la arquitectura conceptual.
* **Fase 2 (Próxima):** Calibración de los cinco pipelines de variación controlable (Stable Diffusion + ControlNet) en Jupyter Notebooks.
* **Fase 3 (Desarrollo UI y Registro):** Construcción de la interfaz gráfica interactiva (Gradio / Streamlit) y almacenamiento de las decisiones del usuario en formato JSON.
* **Fase 4 (Integración y Evaluación):** Conexión del agente LLM para la generación automática de reportes, evaluación de métricas de calidad y diversidad, redacción del informe técnico (máx. 5 páginas) y grabación de la demostración.
