# Nuevas Indicaciones Oficiales del Proyecto 2 (Semana 13)

> **Curso:** CS5363 Planificación y Toma de Decisiones en IA (UTEC 2026-2)  
> **Docente:** Mg. Robert Junior Buleje Del Carpio  
> **Fecha de Emisión:** 9 de noviembre de 2026  
> **Referencia:** Anuncio oficial en Canvas UTEC / Taller de Design Thinking (Semana 13)  

---

## 1. Integración del Taller de Design Thinking

En el informe técnico y sustentación no se requiere una sección completa independiente, pero sí se deben incorporar fragmentos y elementos explícitos que evidencien el proceso mediante el cual se llegó a la versión final del dataproduct:

* **Enfoque Centrado en las Personas:** Combinación de empatía con los usuarios, co-creación y feedback iterativo.
* **Definición del Reto:** Formulación estructurada de la pregunta guía (*¿Cómo podríamos facilitar la generación accesible y controlada de retratos profesionales para estudiantes y jóvenes egresados?*).
* **Perfil de Usuario:** Levantamiento de necesidades profundas, motivaciones profesionales y frustraciones ante herramientas generativas convencionales no controladas.
* **Propuesta de Valor:**
  - *Dimensión Funcional:* Generación rápida de retratos adaptados a las normas visuales de cada red (LinkedIn, WhatsApp corporativo, GitHub).
  - *Dimensión Social:* Proyección de credibilidad y formalidad profesional para reclutadores y clientes.
  - *Dimensión Emocional:* Confianza y tranquilidad del usuario al no distorsionar su fisionomía real.
* **Viaje de Experiencia del Usuario (Journey Map):** Mapeo de la interacción desde el selfie cotidiano inicial, la visualización de bordes Canny, la votación con Aceptar/Rechazar y la retroalimentación explicativa del agente LLM.

---

## 2. Restricciones de Acceso a Khipu y Personalización Técnica

Debido a las limitaciones de acceso al clúster Khipu:

* **Priorización de Tecnologías Gratuitas:** Desarrollar personalización mediante **LoRA (Low-Rank Adaptation)**, StyleGAN o adaptadores similares sobre plataformas gratuitas como **Google Colab (GPU T4)** o **Kaggle**.
* **Nivel Avanzado:** Si se implementa personalización mediante LoRA sobre el modelo de difusión, no es estrictamente indispensable contar con un respaldo de la misma envergadura, ya que la personalización cubre el requerimiento técnico avanzado.

---

## 3. Validación Continua con Usuarios (Mínimo 10 Personas)

La validación del sistema no debe limitarse a un anexo estático:

* **Muestra Requerida:** Pruebas obligatorias con al menos **10 personas** (compañeros de la universidad, familiares o docentes).
* **Rol del Proceso de Evaluación:** La evaluación continua orientó el desarrollo de las funcionalidades de la herramienta (definición de presets por red social, incorporación del prompt libre para vestimenta, ajuste de contraste y simplificación de la votación).
* **Sustento en Datos:** Evidencia cuantitativa y cualitativa de que las imágenes producidas cumplen el objetivo profesional esperado por usuarios reales.

---

## 4. Dinámica de Sustentación y Jurado Evaluador

La evaluación final contará con un jurado multidisciplinario externo (profesionales de la industria y maestría invitados por el docente):

* **Formato de Exposición:**
  - **15 a 20 minutos:** Presentación formal en diapositivas con **demostración de la herramienta en vivo** (imprescindible).
  - **10 minutos:** Ronda de preguntas y evaluación del jurado.
* **Fórmula de Calificación:**
  $$\text{Nota Final} = \frac{\text{Promedio Jurado} + \text{Nota Docente}}{2} \quad (\text{Escala de 0 a 20})$$
* **Criterios de Evaluación del Jurado (Estilo Demoday / Concurso):**
  1. *Problemática:* Claridad en el planteamiento, justificación del problema y motivación real.
  2. *Propuesta Técnica:* Aplicación correcta de herramientas de IA (ControlNet, difusión, LoRA, LLM) y dimensionamiento técnico adecuado.
  3. *Implementación:* Implementación progresiva sustentada en datos, excelente demo en vivo y validación con al menos 10 usuarios.
  4. *Presentación:* Dominio del tiempo asignado (15-20 min), claridad expositiva y soporte visual profesional.
  5. *Preguntas:* Solvencia técnica al responder las consultas del jurado.

---

## 5. Nota Académica Adicional
* El tema de **Propiedad Intelectual** en modelos generativos e IA será evaluado en el examen final del curso.
