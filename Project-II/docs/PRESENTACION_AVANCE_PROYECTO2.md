# Avance Proyecto 2: Sistema Generativo Interactivo para Variaciones Visuales con Feedback Humano y Explicación mediante Agentes de IA

**Curso:** Planificación y Toma de Decisiones en IA (CS5363) — UTEC (2026-2)  
**Profesores:** Dra. Aurea Soriano-Vargas & Mg. Robert Buleje  
**Grupo 7:** Gálvez Pacori, José Guillermo | Meneses Roncal, Matías Alonso | Ore García, Alejandro Joel  
**Caso de Uso:** Asistente Interactivo de Edición y Estilizado de Retratos Profesionales  

---

## 3.1 Definición del Problema y Caso de Uso

### Problema de la Generación Automatizada Pura
Los modelos generativos modernos son capaces de sintetizar imágenes con gran fidelidad visual, pero operan sin contexto sobre las intenciones del usuario, normas institucionales o preferencias estéticas personales. Sin supervisión humana, la generación automática tiende a producir resultados genéricos, desalineados del propósito práctico o que distorsionan la identidad del sujeto.

### Enfoque Metodológico: Human-in-the-Loop
Para resolver esto, el proyecto diseña un sistema de toma de decisiones asistida que combina:
* La capacidad de la IA para explorar rápidamente un espacio amplio de alternativas visuales.
* El criterio contextual del usuario, quien evalúa, acepta o rechaza las opciones generadas.
* Un agente de lenguaje que transparenta y formaliza el proceso de selección mediante explicaciones coherentes.

### Caso de Uso Seleccionado
**Asistente interactivo para la edición y estilizado de fotografías de perfil profesional**. A partir de una fotografía cargada por el usuario, el sistema genera cinco variaciones visuales controladas (iluminación, expresión, fondo, vestimenta y estilo estético) para que el usuario determine qué opciones proyectan mejor su perfil.

---

## 3.1 Diseño General del Sistema (Flujo de Decisiones)

El sistema se compone de cinco bloques articulados:

1. **Módulo de Entrada y Preprocesamiento:** Carga de la imagen original del usuario, detección facial y normalización dimensional.
2. **Módulo Generativo Controlable (2 Enfoques):** Síntesis de exactamente cinco variaciones visuales a partir de la imagen y prompts condicionales.
3. **Interfaz Gráfica e Interacción Humano–IA:** Visualización comparativa de las cinco alternativas. El usuario emite su decisión binaria (Aceptar o Rechazar) por cada opción.
4. **Registro Estructurado de Decisiones:** Almacenamiento de metadatos de las variaciones y respuestas del usuario en un esquema estructurado (JSON).
5. **Agente Basado en LLMs para Explicabilidad:** Procesamiento del registro JSON para emitir un resumen textual coherente que describe y justifica fielmente las opciones aceptadas y rechazadas.

---

## 3.2 Selección y Preparación de Datos

### Dataset de Referencia: CelebA-HQ / Retratos Fotográficos
* **Justificación:** Los retratos constituyen el dominio idóneo para evaluar transformaciones naturales de iluminación, expresión, vestimenta y fondo sin perder la fisonomía base del sujeto.
* **Evaluación:** Permite contrastar los resultados sintéticos frente a imágenes de alta resolución con atributos anotados.

### Técnicas de Preprocesamiento de Entrada
* **Alineación y Recorte Facial:** Centrado del sujeto para estandarizar escala y orientación.
* **Normalización y Redimensionamiento:** Ajuste a resolución estándar (512x512 o 768x768) requerida por los modelos generativos.
* **Extracción de Mapas de Condición:** Detección de pose (OpenPose) y mapas de bordes (Canny) para fijar la estructura anatómica del rostro.

---

## 3.3 Módulo Generativo: 5 Variaciones Visuales (2 Enfoques)

Siguiendo las indicaciones de la cátedra, se implementarán dos enfoques técnicos:

### Enfoques de Implementación
1. **Enfoque Principal (Nivel Intermedio):** Stable Diffusion con `img2img` y ControlNet. Permite modificar atributos específicos preservando la identidad biométrica y estructura del rostro.
2. **Enfoque Alternativo / Respaldo (Nivel Básico):** Generación mediante API preentrenada (SD API o DALL-E) como modo rápido o contingencia ante recursos de cómputo limitados.

### Las 5 Variaciones Visuales
* **Variación 1:** Iluminación de estudio fotográfico profesional.
* **Variación 2:** Expresión facial optimizada (sonrisa corporativa sutil).
* **Variación 3:** Fondo contextual (oficina ejecutiva moderna o neutro difuminado).
* **Variación 4:** Cambio de vestimenta (atuendo formal / corporativo).
* **Variación 5:** Renderizado estético / estilo editorial.

---

## 3.4 Interfaz Gráfica e Interacción Humano–IA

* **Herramienta:** Interfaz web interactiva desarrollada en Gradio o Streamlit.
* **Visualización Comparativa:** Presentación paralela de la fotografía original junto a las cinco opciones generadas de manera simultánea.
* **Mecanismo de Decisión:** Cada imagen cuenta con controles directos e independientes de **Aceptar** y **Rechazar**.
* **Registro Estructurado:** Las decisiones y atributos de cada variación se serializan en un formato JSON estructurado, alimentando directamente al módulo de explicabilidad.

---

## 3.5 Generación de Explicaciones mediante Agente LLM

* **Entrada del Agente:** El registro JSON con las opciones aceptadas y rechazadas, junto con la descripción del cambio aplicado a cada una.
* **Salida del Agente:** Un resumen en lenguaje natural claro y estructurado que explica fielmente qué opciones fueron aceptadas y cuáles rechazadas, sustentando el proceso de selección.
* **Comparación de Modelos:** Se evaluarán dos modelos de lenguaje ligeros (por ejemplo: Gemini 1.5 Flash frente a GPT-4o-mini o Llama-3) para comparar la calidad y coherencia del reporte generado.
* **Criterio de Explicabilidad:** 100% de alineación factual (el agente no debe atribuir decisiones contrarias a las registradas por el usuario).

---

## 2.6 - 2.7 Evaluación, Consideraciones Éticas y Entregables

### Métricas de Evaluación
* **Calidad y Diversidad Visual:** CLIP-Score para alineación semántica y LPIPS / distancia de embeddings para evitar alternativas redundantes.
* **Interacción:** Tasa de aceptación útil por sesión (proporción de opciones aceptadas por el usuario).
* **Coherencia del Agente:** Fidelidad factual entre el JSON de decisiones y el texto explicativo.

### Consideraciones Éticas
* **Privacidad:** Procesamiento efímero de las fotografías cargadas sin almacenamiento persistente ni reutilización sin consentimiento.
* **Mitigación de Sesgos:** Auditoría de los modelos frente a sesgos en tono de piel, género y edad al aplicar transformaciones estéticas.
* **Prevención de Suplantación:** Restricción estricta a la optimización contextual y estética de la propia imagen aportada, impidiendo la generación de deepfakes difamatorios.

### Entregables del Proyecto
1. **Código del Sistema:** Implementación completa y reproducible (generador, UI y agente LLM).
2. **Documento Técnico:** Informe de un máximo de cinco páginas describiendo el ciclo completo.
3. **Demostración:** Video o presentación en vivo evidenciando el funcionamiento interactivo del sistema.
