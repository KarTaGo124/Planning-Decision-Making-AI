# Guión de Exposición: Avance del Proyecto 2

**Curso:** Planificación y Toma de Decisiones en IA — UTEC (2026-2)  
**Grupo 7:** Gálvez Pacori, José Guillermo | Meneses Roncal, Matías Alonso | Ore García, Alejandro Joel  
**Proyecto:** Sistema Generativo Interactivo para Variaciones Visuales con Feedback Humano y Explicación mediante Agentes de IA  
**Tiempo estimado de exposición:** 6 a 8 minutos  

---

## Diapositiva 1: Portada

> *"Buenas tardes profesora Aurea, profesor Robert. Nosotros somos el Grupo 7 y el día de hoy les presentamos el avance y propuesta inicial para nuestro Proyecto 2.*
>
> *El proyecto se titula 'Sistema Generativo Interactivo para Variaciones Visuales con Feedback Humano y Explicación mediante Agentes de IA'. Como caso de uso para aplicar lo solicitado en la guía, hemos elegido desarrollar un Asistente Interactivo de Edición y Estilizado de Retratos Profesionales."*

---

## Diapositiva 2: 3.1 Definición del Problema y Caso de Uso

> *"Comenzando con la definición del problema: hoy en día los modelos generativos pueden crear imágenes muy realistas, pero cuando operan de forma 100% automática tienen una limitación clara: no conocen el contexto real ni el criterio de la persona. En contextos como fotos de perfil o retratos profesionales, una IA que genera por su cuenta muchas veces distorsiona los rasgos de la persona o genera estilos que no encajan con lo que el usuario busca.*
>
> *Por eso, el núcleo de nuestro proyecto es implementar un enfoque 'Human-in-the-Loop', es decir, poner al ser humano en el centro de la decisión. La IA se encarga de explorar y proponer opciones visuales, pero es el usuario quien evalúa y decide qué acepta y qué rechaza.*
>
> *En concreto, el usuario cargará su foto y el sistema le propondrá 5 variaciones específicas pensadas para mejorar su imagen profesional: desde iluminación de estudio hasta cambios de fondo y vestimenta formal."*

---

## Diapositiva 3: 3.1 Diseño General del Sistema (Flujo de Decisiones)

> *"Aquí pueden ver la arquitectura y el flujo general de decisiones que hemos diseñado para el sistema, compuesto por 5 bloques:*
>
> *Primero, la ingesta: el usuario sube su retrato y se hace un preprocesamiento básico para detectar el rostro y normalizarlo.*  
> *Segundo, el módulo generativo: toma esa imagen y produce exactamente las cinco variaciones visuales.*  
> *Tercero, la interfaz gráfica: le muestra al usuario la foto original junto con las cinco opciones para que las compare de forma clara.*  
> *Cuarto, el registro estructurado: cada vez que el usuario marca 'Aceptar' o 'Rechazar', esa decisión se guarda en un archivo JSON con los datos de qué cambio se aplicó a cada imagen.*  
> *Y quinto, el agente LLM: este agente lee ese JSON de decisiones y redacta un resumen en lenguaje natural que explica de manera clara y fiel qué eligió el usuario y por qué."*

---

## Diapositiva 4: 3.2 Selección y Preparación de Datos

> *"En cuanto a los datos, como dataset de referencia utilizaremos CelebA-HQ y bancos de retratos fotográficos de alta calidad.*
>
> *¿Por qué retratos? Porque, tal como sugiere el documento de la cátedra, los rostros son el dominio donde más se notan las variaciones de luz, expresión o fondo, y además nos permite evaluar fácilmente si se respeta o no la identidad de la persona.*
>
> *A nivel de preprocesamiento, para que el modelo funcione bien, aplicaremos detección facial con recorte centrado, redimensionamiento a 512 por 512 o 768 por 768 píxeles, y además extraeremos mapas de control, como la pose con OpenPose o bordes con Canny, que serán clave para guiar la generación sin deformar el rostro."*

---

## Diapositiva 5: 3.3 Módulo Generativo: 5 Variaciones (2 Enfoques)

> *"Para el módulo generativo, siguiendo la indicación de contar con alternativas, hemos mapeado dos enfoques:*
>
> *Nuestro enfoque principal será de Nivel Intermedio: utilizaremos Stable Diffusion con img2img y ControlNet. Esto nos permite condicionar la generación con prompts de texto pero manteniendo fija la estructura del rostro original, logrando un control fino.*  
> *Y como segundo enfoque de respaldo, tendremos el Nivel Básico mediante una API preentrenada, como la API de Stable Diffusion o DALL-E, que servirá como alternativa rápida o contingencia si la máquina no cuenta con GPU suficiente.*
>
> *Con estos modelos generaremos exactamente cinco variaciones controladas:*
> 1. *Iluminación de estudio profesional.*
> 2. *Expresión facial optimizada con una sonrisa sutil.*
> 3. *Cambio de fondo a un entorno corporativo o neutro difuminado.*
> 4. *Cambio a vestimenta ejecutiva formal.*
> 5. *Y un renderizado estético o estilo editorial."*

---

## Diapositiva 6: 3.4 Interfaz Gráfica e Interacción Humano–IA

> *"En la etapa 4, desarrollaremos una interfaz gráfica web utilizando herramientas interactivas como Gradio o Streamlit.*
>
> *La idea es que sea una interfaz limpia y minimalista: el usuario verá su foto original en grande y al lado las cinco variaciones generadas.*
>
> *Debajo de cada opción colocaremos dos botones sencillos: 'Aceptar' y 'Rechazar'. De esta manera el usuario interactúa sin complicaciones, y por detrás el sistema serializa todas estas respuestas en un JSON estructurado que documenta exactamente qué opciones fueron aprobadas y cuáles descartadas."*

---

## Diapositiva 7: 3.5 Generación de Explicaciones mediante Agente LLM

> *"Llegando a la etapa 5, el componente de explicabilidad lo lidera el agente basado en LLMs.*
>
> *Este agente recibe directamente el JSON con las decisiones del usuario. Su tarea no es inventar cosas, sino traducir esas elecciones a un reporte coherente en lenguaje natural: explicará explícitamente cuáles se aceptaron, cuáles se rechazaron y resumirá el perfil de preferencia del usuario.*
>
> *Además, para comparar resultados como sugiere la cátedra, planeamos probar dos modelos de lenguaje ligeros, por ejemplo Gemini Flash frente a GPT-4o-mini o Llama-3, asegurando siempre que la métrica de coherencia factual sea del 100%, es decir, que el agente nunca diga que se aceptó una opción que el usuario rechazó."*

---

## Diapositiva 8: 2.6 - 2.7 Evaluación, Ética y Entregables

> *"Finalmente, para cerrar la propuesta:*
>
> *A nivel de evaluación, mediremos la calidad visual y alineación con CLIP-Score, la diversidad entre las 5 opciones con LPIPS para evitar que salgan repetidas, la tasa de aceptación en la interfaz y la coherencia del agente.*
>
> *En el aspecto ético, garantizamos la privacidad de las fotos: el procesamiento será temporal y no almacenaremos fotos de usuarios en servidores externos ni se usarán para reentrenar modelos. Además, el sistema está acotado estrictamente a estilizado profesional, previniendo cualquier uso malicioso o deepfake.*
>
> *Con esto completamos las 5 etapas del proyecto. Nuestro entregable final incluirá el código funcional del pipeline, el informe técnico de máximo 5 páginas y un video demostrativo del sistema completo funcionando.*
>
> *Quedamos atentos a sus preguntas y sugerencias para orientar el desarrollo. Muchas gracias."*
