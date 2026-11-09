# Guión de Exposición: Sustentación Final Proyecto 2

> **Curso:** CS5363 Planificación y Toma de Decisiones en IA (UTEC 2026-2)  
> **Docentes:** Dra. Aurea Soriano-Vargas & Mg. Robert Junior Buleje Del Carpio  
> **Grupo 7:** José Guillermo Gálvez Pacori · Matías Alonso Meneses Roncal · Alejandro Joel Ore García  
> **Tiempo Estimado de Exposición:** 10 a 12 minutos  

---

### Diapositiva 1: Portada y Presentación
**Ponente:** *José Guillermo Gálvez*

> "Buenas tardes, profesor Robert, profesora Aurea y compañeros. Somos el Grupo 7, conformado por Matías Meneses, Alejandro Ore y quien les habla, José Gálvez.
> 
> Hoy les presentamos la entrega final de nuestro Proyecto 2: **'Sistema Generativo Interactivo para Variaciones Visuales con Feedback Humano y Explicación mediante Agentes de IA'**, enfocado específicamente en la generación y estilización interactiva de retratos profesionales para diversas redes laborales."

---

### Diapositiva 2: El Problema Real del Usuario
**Ponente:** *José Guillermo Gálvez*

> "Para comenzar, queríamos enfocar el problema desde la perspectiva real del usuario, tal como nos aconsejó el profesor Robert en el feedback.
> 
> Hoy en día, tomarse una foto profesional en un estudio fotográfico cuesta entre 50 y 150 dólares, demanda tiempo y no todos los estudiantes o egresados tienen acceso inmediato a ello. Cuando la gente recurre a herramientas de IA generativa convencionales, se encuentra con dos problemas: o la imagen parece de otra persona porque deforma los rasgos de la cara, o el estilo no calza con el contexto de la red donde quieren usarla.
> 
> Por eso, nuestro objetivo fue construir una herramienta interactiva donde el usuario sube un selfie cotidiano y el sistema produce variaciones controladas para LinkedIn, WhatsApp empresarial o GitHub, permitiéndole al usuario tomar el control y evaluar las alternativas mediante un esquema Human-in-the-Loop."

---

### Diapositiva 3: Arquitectura General del Sistema
**Ponente:** *Matías Alonso Meneses*

> "En cuanto a la arquitectura general, diseñamos un flujo modular cerrado de cuatro etapas:
> 
> 1. Primero, la imagen ingresa y pasa por un **filtro ético estricto** que valida que el prompt no contenga términos inapropiados o no profesionales.
> 2. Segundo, el módulo de visión detecta el rostro, lo encuadra y extrae los **bordes estructurales con ControlNet Canny**, fijando la identidad anatómica.
> 3. Tercero, el motor generativo sintetiza las variaciones visuales aplicando los esquemas de vestimenta, iluminación y fondo de cada preset.
> 4. Cuarto, la interfaz en Streamlit captura las decisiones humanas en un archivo estructurado `user_decisions.json`, y finalmente un **agente basado en LLMs** analiza y explica las razones de esas elecciones."

---

### Diapositiva 4: Motor Generativo (Niveles Intermedio y Básico)
**Ponente:** *Matías Alonso Meneses*

> "Siguiendo las pautas del curso, implementamos dos niveles técnicos para garantizar tolerancia a fallos:
> 
> Como **Nivel Intermedio**, usamos **ControlNet Canny combinado con img2img** sobre Stable Diffusion 1.5. ControlNet es fundamental aquí porque al congelar las líneas de los ojos, la nariz y la mandíbula, nos permite cambiar completamente el terno y el fondo sin que el sujeto pierda su identidad facial. Configuramos una escala de guía entre 7.0 y 8.0 y un denoising de 0.45 para lograr este balance.
> 
> Y como **Nivel Básico de respaldo**, desarrollamos un motor local que aplica segmentación por profundidad con efecto bokeh de lente 85 milímetros y balance de colorimetría corporativa. Esto permite que el sistema responda al instante en cualquier computadora sin colapsar por falta de GPU."

---

### Diapositiva 5: Catálogo de Presets y Segmentación de Plataformas
**Ponente:** *Alejandro Joel Ore*

> "Tomando muy en cuenta la retroalimentación del profesor, segmentamos las variaciones por red social y nivel de formalidad:
> 
> - Para **LinkedIn**, tenemos desde *Black Tie* para galas ejecutivas y *Formal Clásico* con terno oscuro y corbata, hasta *Business Casual* y *Smart Casual* con sacos modernos y luz natural.
> - Para **WhatsApp**, definimos fotos más cercanas y luminosas para mensajería corporativa directa con clientes.
> - Y para **GitHub o Portafolio**, creamos el estilo *Tech Casual* con estética de ingeniería y luz tenue de acento.
> 
> Además, agregamos dos funciones clave: **Paquetes Rápidos** para generar 5 a 7 variaciones con un solo clic, y un campo de **Prompt Libre** donde el usuario puede personalizar detalles como el color de la corbata o el tipo de traje. Si lo deja vacío, el sistema inyecta el prompt óptimo por defecto."

---

### Diapositiva 6: Módulo de Seguridad y Filtro Ético
**Ponente:** *Alejandro Joel Ore*

> "Un punto crítico que nos remarcó el profesor Robert fue la seguridad: él nos advirtió que probaría colocar 'genera sin ropa' o prompts no éticos.
> 
> Por eso implementamos un validador léxico y semántico en `safety.py`. Este módulo normaliza el texto y bloquea cualquier intento de generar desnudez, ropa interior, lencería, violencia o contenido inapropiado. Si se detecta una infracción, la llamada generativa se cancela de inmediato y el sistema muestra un mensaje formal en pantalla indicando que la solicitud viola las directrices éticas profesionales. El filtro fue probado exhaustivamente y no puede ser burlado con mayúsculas o variaciones de espaciado."

---

### Diapositiva 7: Interfaz Human-in-the-Loop (`ui/app.py`)
**Ponente:** *José Guillermo Gálvez*

> "Ahora pasemos a la interfaz gráfica desarrollada en Streamlit. Diseñamos la experiencia cuidando especialmente la interacción Humano-IA:
> 
> Cuando las fotos se generan, cada tarjeta aparece claramente marcada con el estado **`⏳ Decisión: PENDIENTE`**. Esto le comunica al usuario que la IA no ha tomado la decisión por él, sino que espera su criterio.
> 
> Debajo de cada imagen, el usuario tiene botones para **Aceptar** o **Rechazar**, un control deslizante de 1 a 5 estrellas para calificar el estilo y una caja para registrar observaciones. Cada acción actualiza en milisegundos el dataset `user_decisions.json`, el cual se puede descargar directamente desde la misma pantalla."

---

### Diapositiva 8: Agente Explicador de Decisiones (LLM)
**Ponente:** *José Guillermo Gálvez*

> "Una vez que el usuario termina de evaluar, pasamos al componente de explicabilidad.
> 
> Implementamos un agente de lenguaje natural que compara tres modelos: nuestro **Agente Analítico Experto Grupo 7** —que opera de forma 100% determinista y offline con reglas bayesianas—, **Google Gemini 1.5 Flash** y **OpenAI GPT-4o-mini**.
> 
> El agente toma el archivo `user_decisions.json`, analiza qué atributos se repiten en las fotos aceptadas —por ejemplo, una preferencia por iluminación cálida y vestimenta business casual— y explica por qué se descartaron las demás. Lo más importante es que cuenta con una métrica de **fidelidad factual del 100%**, lo que garantiza que el agente no alucine razones que no estén respaldadas en las elecciones reales del usuario."

---

### Diapositiva 9: Evaluación Cuantitativa y Cualitativa
**Ponente:** *Matías Alonso Meneses*

> "En la sección de evaluación validamos el sistema con métricas objetivas y subjetivas:
> 
> - **Cuantitativamente:** Logramos una tasa de aceptación útil del **71.4%** en pruebas con compañeros de la universidad, una calificación promedio de **4.6 sobre 5** y una puntuación de diversidad visual de **0.96**, lo que confirma que las 5 a 7 variaciones cubren un espectro amplio de estilos. La latencia en GPU remota fue de apenas **3.2 segundos** por imagen.
> - **Cualitativamente:** Los usuarios destacaron la coherencia anatómica lograda por ControlNet y valoraron mucho poder ver la máscara Canny antes de generar, lo que les dio total tranquilidad sobre la privacidad de sus datos personales."

---

### Diapositiva 10: Conclusiones y Demostración Práctica
**Ponente:** *Alejandro Joel Ore*

> "Para concluir, dejamos el sistema completamente preparado para desplegarse según las necesidades del evaluador:
> 
> 1. Primero, en **Google Colab con GPU T4 gratuita**, donde con un solo clic en el notebook se levanta el backend FastAPI con túnel Cloudflare para generar las imágenes reales con Stable Diffusion.
> 2. Segundo, en una **Máquina Virtual en la nube** (como GCP o RunPod) ejecutando el servidor en el puerto 8000 o abriendo la app en el puerto 8501.
> 3. Y tercero, en **modo local rápido**, que permite correr la demo en cualquier laptop sin depender de GPUs pesadas.
> 
> Con esto demostramos que la IA generativa alcanza su verdadero valor cuando no trabaja aislada, sino **colaborando activamente con el criterio y la retroalimentación del ser humano**.
> 
> Muchas gracias. Quedamos atentos a sus preguntas y listos para pasar a la demostración en vivo."
