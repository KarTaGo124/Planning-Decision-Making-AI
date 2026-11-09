# Guión de Exposición: Sustentación Final Proyecto 2

> **Curso:** CS5363 Planificación y Toma de Decisiones en IA (UTEC 2026-2)  
> **Docentes:** Dra. Aurea Soriano-Vargas & Mg. Robert Junior Buleje Del Carpio  
> **Grupo 7:** José Guillermo Gálvez Pacori · Matías Alonso Meneses Roncal · Alejandro Joel Ore García  
> **Tiempo de Exposición:** 15 a 20 minutos (Demoday: exposición + demo en vivo) + 10 minutos de evaluación del jurado multidisciplinario  

---

### Diapositiva 1: Portada y Presentación
**Ponente:** *José Guillermo Gálvez*

> "Buenas tardes, profesor Robert, profesora Aurea, miembros del jurado evaluador y compañeros. Somos el Grupo 7, integrado por Matías Meneses, Alejandro Ore y quien les habla, José Gálvez.
> 
> Hoy les presentamos la sustentación final de nuestro Proyecto 2: **'Sistema Generativo Interactivo para Variaciones Visuales con Feedback Humano y Explicación mediante Agentes de IA'**, enfocado específicamente en la estilización y adaptación inteligente de retratos profesionales para diversas redes laborales."

---

### Diapositiva 2: El Problema Real y Metodología Design Thinking
**Ponente:** *José Guillermo Gálvez*

> "Para comenzar, abordamos el problema aplicando la metodología de Design Thinking impartida en el taller de la diseñadora Andrea Alarcón en la Semana 13.
> 
> Partimos formulando el reto de diseño: *'¿Cómo podríamos facilitar a los estudiantes y egresados de UTEC la obtención de fotografías profesionales de alta calidad, contextualizadas a distintas plataformas laborales, sin incurrir en elevados costos de estudio fotográfico ni perder su identidad anatómica facial?'*
> 
> A partir de ello, estructuramos nuestra propuesta de valor en tres dimensiones:
> 
> 1. **Dimensión Funcional:** Generar retratos fotorrealistas con iluminación de estudio y vestimenta adecuada para LinkedIn, WhatsApp corporativo y GitHub, preservando intacta la identidad anatómica del usuario.
> 2. **Dimensión Social:** Permitir al usuario proyectar una imagen de seriedad, empleabilidad y profesionalismo acorde a los estándares de cada industria y red laboral.
> 3. **Dimensión Emocional:** Reducir la ansiedad y otorgar seguridad y confianza personal al momento de postular a prácticas preprofesionales y procesos de selección.
> 
> A través del User Journey Map identificamos que el dolor principal al recurrir a herramientas generativas convencionales era doble: la pérdida de identidad facial —donde la persona no se reconocía a sí misma— y la falta de adecuación estilística. Por ello concebimos una herramienta interactiva Human-in-the-Loop donde el usuario retiene el control absoluto de sus elecciones."

---

### Diapositiva 3: Arquitectura General del Sistema
**Ponente:** *Matías Alonso Meneses*

> "En cuanto a la arquitectura general, diseñamos un flujo modular cerrado de cuatro etapas:
> 
> 1. Primero, la imagen ingresa y pasa por un **filtro ético y de seguridad léxica** que valida que el prompt no contenga términos inapropiados o no profesionales.
> 2. Segundo, el módulo de visión detecta el rostro, lo encuadra y extrae los **bordes estructurales con ControlNet Canny**, fijando la identidad anatómica de las facciones.
> 3. Tercero, el motor generativo sintetiza las variaciones visuales aplicando los esquemas de vestimenta, iluminación y fondo corporativo de cada preset.
> 4. Cuarto, la interfaz en Streamlit captura las decisiones humanas en un archivo estructurado `user_decisions.json`, y finalmente un **agente basado en LLMs** analiza y explica las razones de esas elecciones."

---

### Diapositiva 4: Motor Generativo y Adaptación ante Restricciones de Cómputo
**Ponente:** *Matías Alonso Meneses*

> "Siguiendo las directrices del curso y las indicaciones del profesor Robert respecto a las restricciones de acceso al cluster Khipu, priorizamos el desarrollo de un pipeline accesible y eficiente en Google Colab con GPU T4 gratuita:
> 
> Como **Nivel Intermedio y Avanzado**, implementamos **ControlNet Canny combinado con img2img y soporte para adaptadores LoRA (Low-Rank Adaptation)** sobre Stable Diffusion 1.5. ControlNet es la pieza angular de nuestra solución: al congelar las líneas de los ojos, la nariz y la mandíbula, nos permite cambiar completamente el terno y el fondo sin que el sujeto pierda su identidad facial. La técnica LoRA nos permite modular estilos fotográficos corporativos sin la necesidad de reentrenar modelos pesados en clusters cerrados. Configuramos una escala de guía entre 7.0 y 8.0 y un denoising de 0.45 para balancear fotorrealismo e identidad.
> 
> Y como **Nivel Básico de respaldo**, desarrollamos un motor local que aplica segmentación por profundidad con efecto bokeh de lente 85 milímetros y balance de colorimetría corporativa. Esto permite que el sistema responda al instante en cualquier computadora sin colapsar por falta de GPU."

---

### Diapositiva 5: Catálogo de Presets y Segmentación de Plataformas
**Ponente:** *Alejandro Joel Ore*

> "Tomando muy en cuenta la retroalimentación del profesor, segmentamos las variaciones por red social y nivel de formalidad:
> 
> - Para **LinkedIn**, tenemos desde *Black Tie* para galas ejecutivas y *Formal Clásico* con terno oscuro y corbata, hasta *Business Casual* y *Smart Casual* con sacos modernos y luz natural de ventana.
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
> Cuando las fotos se generan, cada tarjeta aparece claramente marcada con el estado **`Decisión: Pendiente`**. Esto le comunica al usuario que la IA no ha tomado la decisión por él, sino que espera su criterio.
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

### Diapositiva 9: Evaluación Cuantitativa y Validación Continua con Usuarios
**Ponente:** *Matías Alonso Meneses*

> "Siguiendo las pautas del profesor, la validación del sistema no se limitó a un reporte estático, sino que realizamos pruebas continuas con 10 personas reales: estudiantes de ingeniería de UTEC, docentes y egresados.
> 
> En el plano cuantitativo obtuvimos:
> - Una tasa de aceptación del **70.0%** (35 de 50 variaciones aceptadas).
> - Una calificación promedio de **4.60 sobre 5.0**.
> - Preservación anatómica validada por el **100%** de los participantes (10 de 10).
> - Diversidad visual calculada en **0.96**.
> - Latencia en GPU remota de **3.2 segundos** por imagen.
> 
> Y en el plano del diseño del producto, las pruebas con usuarios guiaron tres evoluciones directas de la herramienta:
> 1. La creación de presets específicos para WhatsApp tras el pedido de los evaluadores para comunicarse profesionalmente con clientes.
> 2. La incorporación del campo de Prompt Libre para dar flexibilidad en accesorios y tonalidades sin perder la coherencia corporativa.
> 3. La insignia explícita 'Decisión: Pendiente', surgida porque los usuarios expresaron la necesidad de saber con certeza que ninguna decisión quedaba preestablecida por la IA."

---

### Diapositiva 10: Conclusiones y Demostración Práctica (Demoday)
**Ponente:** *Alejandro Joel Ore*

> "Para concluir, nuestra propuesta responde a los cinco criterios de evaluación del jurado del Demoday: problemática justificada en Design Thinking, propuesta técnica accesible y dimensionada, e implementación progresiva validada con usuarios reales.
> 
> El sistema está completamente preparado para desplegarse de tres formas según las condiciones de la sala:
> 1. Primero, en **Google Colab con GPU T4 gratuita**, levantando el backend FastAPI con túnel Cloudflare para generar las imágenes reales en segundos.
> 2. Segundo, en una **Máquina Virtual en la nube** (como GCP o RunPod) ejecutando el servidor en el puerto 8000 y Streamlit en el 8501.
> 3. Y tercero, en **modo local rápido**, que permite correr la demo en cualquier laptop sin depender de conexión a GPU externa.
> 
> Con esto demostramos que la IA generativa alcanza su verdadero potencial cuando no opera como una caja negra aislada, sino **colaborando activamente con el criterio y la retroalimentación del ser humano**.
> 
> Pasamos ahora a la demostración en vivo de la aplicación. Muchas gracias y quedamos atentos a las preguntas del jurado."
