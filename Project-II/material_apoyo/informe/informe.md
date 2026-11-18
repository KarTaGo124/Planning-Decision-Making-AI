<div class="portada">
<p class="inst">Universidad de Ingeniería y Tecnología (UTEC) · Departamento de Ciencia de la Computación</p>
<h1>Retratos profesionales controlados: sistema generativo interactivo con feedback humano y agente explicador</h1>
<p class="sub">Proyecto 2 · CS5363 Planificación y Toma de Decisiones en IA · 2026-2</p>
<p class="meta"><b>Grupo 7:</b> José Guillermo Gálvez Pacori · Matías Alonso Meneses Roncal · Alejandro Joel Ore García<br>
<b>Docentes:</b> Dra. Aurea Soriano-Vargas · Mg. Robert Junior Buleje Del Carpio<br>
<b>Repositorio:</b> https://github.com/KarTaGo124/Planning-Decision-Making-AI (carpeta <code>Project-II</code>)</p>
</div>

**Resumen.** Construimos un sistema que recibe una foto del usuario, genera cinco variaciones de retrato profesional adaptadas a LinkedIn, WhatsApp corporativo o GitHub, deja que el usuario acepte o rechace cada una y usa un agente basado en un modelo de lenguaje para explicar qué eligió y por qué. Implementamos dos formas de generar: Stable Diffusion 1.5 con ControlNet Canny en modo img2img (nivel intermedio) y Stable Diffusion 1.5 img2img sin ControlNet (nivel básico), ambas con un LoRA público, en una GPU T4 gratuita de Google Colab y conectadas a una interfaz Streamlit. Medimos latencia, diversidad, cambio de identidad y fidelidad del agente. El agente alcanzó 100 % de fidelidad en 10 corridas. El hallazgo principal es una limitación: con la intensidad necesaria para cambiar la ropa, el modelo altera rasgos de identidad como la textura del pelo. Lo documentamos como sesgo y proponemos la mejora.

## 1. Problema y contexto

Un retrato profesional pesa en la empleabilidad, pero una sesión de estudio cuesta entre 50 y 150 USD y exige tiempo y traslados. Los generadores de imágenes de uso general ofrecen una alternativa barata con tres problemas: no conservan con fidelidad la cara del usuario, no distinguen el nivel de formalidad que espera cada red (un perfil de LinkedIn no es una foto de WhatsApp para clientes) y no explican por qué producen lo que producen.

En el taller de Design Thinking de la semana 13 enmarcamos el reto con la pregunta guía: *¿cómo podríamos facilitar la generación accesible y controlada de retratos profesionales para estudiantes y jóvenes egresados?* El perfil de usuario que definimos es un estudiante de ciclos avanzados o egresado reciente que busca prácticas o su primer empleo. Tiene presupuesto limitado, teme que la IA lo deforme o lo haga verse artificial y no conoce los códigos visuales de cada red.

La propuesta de valor tiene tres dimensiones:

- **Funcional:** cinco variaciones con estilos predefinidos por red social y la opción de ajustar la vestimenta con texto libre.
- **Social:** una imagen creíble ante reclutadores y clientes.
- **Emocional:** la tranquilidad de verse a uno mismo y entender por qué el sistema propone cada opción.

El recorrido del usuario (*journey map*) que guía el diseño es: sube una selfie cotidiana; ve los bordes faciales que guiarán al modelo; recibe cinco opciones en estado *Pendiente*; acepta o rechaza cada una con calificación y comentario; y lee la explicación del agente.

**Objetivo.** Diseñar un sistema de decisión que integre generación, interacción y explicación: exactamente cinco variaciones por imagen, registro estructurado de las decisiones y un resumen fiel a ellas.

**Restricciones.** Sin acceso al clúster Khipu, todo debía correr en recursos gratuitos (GPU T4 de Colab, 15 GB). El sistema no debe generar contenido no profesional ni exponer las fotos de los usuarios.

## 2. Diseño del sistema

<figure><img src="figuras/fig1_arquitectura.png" style="width:100%"><figcaption>Figura 1. Arquitectura y flujo de información. Las decisiones del usuario (paso 5) son la entrada del agente (paso 7).</figcaption></figure>

El sistema separa la interfaz, que corre en la computadora del usuario, del motor generativo, que corre en la GPU (Figura 1):

1. **Filtro ético** (`safety.py`): revisa el texto libre antes de cualquier cómputo y bloquea términos de desnudez, ropa inapropiada, violencia, drogas y odio.
2. **Preproceso** (`generator.py`): detecta la cara, recorta un cuadrado de 512 × 512 px centrado en ella y extrae los bordes Canny.
3. **Motor generativo** (`diffusion.py`, `gpu_server.py`): un servidor FastAPI en Colab recibe la imagen en base64 y devuelve las cinco variaciones. Se expone a internet con un túnel gratuito de Cloudflare.
4. **Interfaz** (`ui/app.py`, Streamlit): muestra las variaciones, registra cada decisión en `user_decisions.json` y guarda cada lote de imágenes con sus tiempos.
5. **Agente explicador** (`agent.py`): resume las decisiones con un modelo de lenguaje. El módulo `evaluator.py` contrasta ese resumen con el registro.

**Decisiones de diseño.**

- **Separar la interfaz de la GPU** permite usar la aplicación desde cualquier laptop. Si la GPU no está disponible, queda un modo de contingencia local que solo aplica filtros de OpenCV; lo declaramos como no generativo y sirve para probar la interfaz.
- **El catálogo tiene 8 estilos y 3 paquetes:** dos paquetes de 5 variaciones y uno de 7 para uso exploratorio. Para la evaluación y la demostración usamos el paquete "Corporativo Multiplataforma", de 5 variaciones, como pide el enunciado. Cada estilo define la vestimenta, la iluminación, el fondo y los parámetros de generación.

## 3. Datos y preprocesamiento

El sistema no entrena un modelo desde cero, así que no usa un dataset de entrenamiento propio. Los datos que procesa son de dos tipos:

- **Fotos de entrada:** las sube el usuario y se usan con su consentimiento.
- **Datos de los modelos preentrenados:** Stable Diffusion 1.5 se entrenó con LAION-5B, un conjunto de pares imagen-texto extraídos de la web. Ese origen explica sesgos que observamos en la sección 7.

Elegimos rostros porque el caso de uso lo exige y porque permiten evaluar a simple vista la conservación de la identidad, como sugiere el enunciado.

**Análisis de las fotos de entrada.** Probamos dos selfies de un integrante del equipo, tomadas con celular:

| Foto | Resolución | Encuadre | Ancho de la cara / ancho de la foto | Detección facial |
|---|---|---|---|---|
| A | 1200 × 1600 | Muy cercana, tomada desde abajo, sin hombros | 85 % | Falló con la configuración inicial |
| B | 899 × 1600 | Pecho hacia arriba, a la altura de los ojos | 55 % | Correcta |

La foto A dejaba casi sin espacio para la ropa y además mostró dos fallas del preprocesamiento, que corregimos (sección 8). Desde entonces usamos la foto B como entrada de referencia. A partir de este análisis definimos la guía de captura que damos al usuario: a la altura de los ojos, a un metro de distancia, de pecho hacia arriba, con fondo liso y sin audífonos.

**Preprocesamiento** (Figura 2):

1. **Rotación:** se corrige la orientación EXIF de las fotos de celular.
2. **Detección facial:** se reduce la imagen a 640 px, se ecualiza el histograma y se prueban dos clasificadores Haar (Viola-Jones).
3. **Recorte:** se recorta un cuadrado de 1,9 veces el tamaño de la cara, que nunca corta la parte superior de la cabeza, y se escala a 512 × 512 px, la resolución nativa de SD 1.5.
4. **Bordes:** se extraen los bordes Canny (umbrales 100 y 200, tras un suavizado gaussiano de 3 × 3), que fijan la geometría de ojos, nariz, boca y mandíbula.

<figure><img src="figuras/fig2_entrada_preprocesamiento.png" style="width:78%"><figcaption>Figura 2. Foto B original, recorte de 512 × 512 px y mapa de bordes Canny que condiciona a ControlNet.</figcaption></figure>

## 4. Modelos generativos

Cumplimos la condición de implementar dos de los tres niveles del enunciado, de modo que funcionen como alternativas y el usuario elija desde la interfaz:

- **Nivel intermedio (enfoque principal).** Usa Stable Diffusion 1.5 (`stable-diffusion-v1-5/stable-diffusion-v1-5`) con ControlNet Canny (`lllyasviel/control_v11p_sd15_canny`) en modo img2img. La foto se usa como punto de partida y los bordes Canny se usan como condición estructural, con una escala de condicionamiento de 0,85.
- **Nivel básico (alternativa).** Usa Stable Diffusion 1.5 en modo img2img sin ControlNet (en el sentido de SDEdit). Comparte la UNet, el VAE y el codificador de texto con el nivel intermedio, así que no ocupa memoria adicional en la GPU.

**Parámetros comunes:** 25 pasos con el planificador UniPC, *guidance scale* de 7,0 a 8,0 y *strength* de 0,40 a 0,50 según el estilo. Para comparar entre métodos se usan semillas fijas (1234 más el índice de la variación).

Los textos de condicionamiento están en inglés, que es el idioma de entrenamiento del codificador CLIP, y miden entre 35 y 43 tokens, por debajo del límite de 77. El texto libre del usuario se antepone a la descripción del estilo, después de pasar el filtro ético.

**Personalización con LoRA.** Por las restricciones de acceso a Khipu, el docente indicó priorizar la personalización con LoRA en plataformas gratuitas. Integramos el LoRA público `OedoSoldier/detail-tweaker-lora` (`add_detail.safetensors`, escala 0,6), que mejora el nivel de detalle en SD 1.5. LoRA congela los pesos del modelo y aprende una actualización de bajo rango, ΔW = BA, sobre las capas de atención. Por eso se carga en segundos y casi no ocupa memoria. El adaptador se puede activar o desactivar en cada petición para comparar resultados.

En la primera corrida en Colab el LoRA no cargó por un conflicto de versiones de torchao: Colab trae preinstalada la versión 0.10.0 y la librería `peft` exige una superior a 0.16.0. El notebook final desinstala `torchao` antes de cargar los modelos. Con ese cambio, en la segunda corrida el LoRA cargó (384 capas en la UNet y 144 en el codificador de texto) y se aplicó a todas las variaciones. La sección 7 compara ambas corridas.

**Despliegue.** El notebook `controlnet_portrait_pipeline.ipynb` se ejecuta con "Ejecutar todas". Instala dependencias, sube la foto, genera los experimentos de la sección 7, descarga un zip con las imágenes y métricas, y deja el servidor GPU publicado con una URL de Cloudflare que se pega en la interfaz.

## 5. Interfaz e interacción humano–IA

<figure><img src="figuras/fig6_interfaz_votacion.png" style="width:86%"><figcaption>Figura 3. Interfaz conectada a la GPU de Colab: foto de entrada y variaciones con su decisión, calificación y comentario.</figcaption></figure>

La interfaz (Figura 3) sigue el flujo de la sección 1:

- **Selección de estilos:** la barra lateral permite elegir el motor (intermedio, básico o contingencia local), un paquete temático o una selección manual de estilos, y escribir un ajuste de vestimenta en texto libre.
- **Filtro inmediato:** el filtro ético revisa ese texto mientras se escribe y bloquea la solicitud con un mensaje explícito (Anexo B).
- **Decisión pendiente:** cada variación aparece con su estilo, la iluminación, el fondo y la vestimenta propuestos, y en estado **Pendiente**. El sistema no asume ninguna aprobación hasta que el usuario vota.
- **Retroalimentación por imagen:** botones *Aceptar* y *Rechazar*, una calificación de 1 a 5 y un comentario.

Cada acción se guarda de inmediato en `data/processed/user_decisions.json`, que se puede descargar desde la pantalla. Cada registro incluye la variación, el estilo, la decisión, la calificación, el comentario, el motor usado y la latencia medida (Anexo C). Cada lote generado se guarda en `data/processed/generated/` con la entrada, los bordes, las cinco imágenes y sus tiempos. La barra lateral también permite asociar las decisiones a un código anónimo de participante y cerrar la sesión en un archivo independiente.

Completar el ciclo toma nueve acciones: subir la foto, elegir el paquete, generar, votar cinco veces y pedir la explicación. Con la GPU de Colab, el tiempo de espera es de 25 a 35 s por lote de cinco imágenes, más 4 a 20 s del agente.

## 6. Agente explicador

El agente (Figura 4) recibe el registro de decisiones y produce primero una lista determinista de las variaciones aceptadas y rechazadas, con su calificación y comentario. Esa lista proviene del JSON y no del modelo de lenguaje, lo que garantiza que el requisito central del enunciado se cumpla siempre. Después pide al modelo de lenguaje una explicación con cuatro secciones: conteos, cada aceptada con su motivo, cada rechazada con su motivo y recomendaciones para la siguiente generación. Las instrucciones exigen usar solo los datos entregados y no omitir ninguna variación.

<figure><img src="figuras/fig7_agente.png" style="width:62%"><figcaption>Figura 4. Explicación generada por Gemini 3.5 Flash Lite para las decisiones de la Figura 3, con su fidelidad calculada y las métricas de la sesión.</figcaption></figure>

Siguiendo la sugerencia de comparar más de un modelo de lenguaje, el agente ofrece tres opciones:

- **Gemini 3.5 Flash Lite** (API de Google), con una cadena de respaldo: Gemini 3.1 Flash Lite, Flash Lite Latest y Gemini 3.8 Flash. Reintenta ante errores 429 y 503 y pasa al siguiente modelo si uno no responde en 25 s.
- **GPT-4o-mini** (API de OpenAI). Está implementado, pero no lo evaluamos por no contar con una clave de API.
- **Agente de reglas** sin conexión, que agrega estadísticas de plataforma, formalidad e iluminación.

Si ningún modelo responde, el sistema usa el agente de reglas y lo informa en pantalla junto con el motivo.

**Fidelidad.** `evaluator.py` comprueba que cada título votado aparezca asociado a su decisión correcta y que estén los tres conteos (total, aceptadas y rechazadas):

<p class="formula">Fidelidad = (comprobaciones correctas) / (número de variaciones votadas + 3)</p>

La métrica se calcula sobre cada explicación y se muestra al usuario. No es una constante.

## 7. Evaluación y resultados

Todas las mediciones se hicieron en una Tesla T4, con la foto B, el paquete de 5 variaciones, 25 pasos y semillas fijas. Hicimos dos corridas con la misma configuración: la primera sin LoRA, por el conflicto descrito en la sección 4, y la segunda con LoRA. Los scripts y los datos crudos están en `material_apoyo/informe/`.

| Métrica | Definición | Intermedio sin LoRA | Intermedio con LoRA | Básico sin LoRA | Básico con LoRA |
|---|---|---|---|---|---|
| Latencia en la GPU | Segundos por imagen | 2,61 s | 2,88 s | 1,96 s | 2,28 s |
| Diversidad visual | Diferencia media absoluta entre pares de imágenes (0–1) | 0,036 | 0,038 | 0,040 | 0,041 |
| Detalle | Varianza del Laplaciano (entrada: 86,9) | 101,8 | 102,5 | 100,4 | 101,7 |
| Cambio de luminosidad de la piel | ΔL\* medio en el centro de la cara (escala 0–100) | −0,39 | −0,43 | −0,35 | −0,44 |
| Diferencia de color de la piel | ΔE medio en el centro de la cara | 1,87 | 1,95 | 2,14 | 2,30 |

Ninguna de las 30 imágenes fue marcada por el filtro de contenido de SD. Desde la app, un lote de 5 tarda entre 25 y 35 s de extremo a extremo, contando la red.

<figure><img src="figuras/fig3_intermedio.png" style="width:100%"><figcaption>Figura 5. Nivel intermedio (ControlNet Canny + img2img) sin LoRA: entrada y las 5 variaciones del paquete corporativo. Con LoRA el resultado es prácticamente igual. El nivel básico se muestra en el Anexo A.</figcaption></figure>

**Calidad y diversidad.**

- **Calidad:** las imágenes son fotorrealistas, sin artefactos graves ni deformaciones faciales, y conservan pose, encuadre y expresión.
- **Diversidad baja:** con *strength* entre 0,42 y 0,48 la ropa cambia poco. El color y el corte de la polera original se mantienen. Solo "Business Casual" muestra un blazer y "Smart Casual Cercano" agrega un cuello de polo; en "Formal Clásico" no aparece el terno. La diferencia media entre variaciones (0,036 a 0,040) confirma que se parecen mucho entre sí.
- **Comparación entre métodos:** con la misma semilla, los dos niveles producen resultados muy parecidos. Con esta intensidad, la imagen de partida pesa más que el condicionamiento de ControlNet, y el nivel básico es entre un 21 % y un 25 % más rápido.

**Intensidad frente a identidad.** El barrido de *strength* (Figura 6) muestra el compromiso central del sistema:

- **Ropa:** el terno aparece a partir de 0,60.
- **Pelo:** con esa intensidad cambia de liso a crespo. El mismo cambio aparece en 2 de las 5 variaciones del paquete ("LinkedIn Smart Casual" y "WhatsApp Business Casual") y en los dos métodos.
- **Rasgos:** con 0,60 y 0,75 también cambian la nariz y los labios, y la persona deja de ser reconocible.
- **Color del terno:** en "Formal Clásico", el "azul marino" del texto tiñe el pelo.
- **Piel:** el cambio es pequeño (ΔL\* medio de −0,4 en el centro de la cara; hasta −2,2 en la cara completa con *strength* de 0,60 a 0,75). No es el efecto dominante.

Interpretamos el cambio de textura del pelo como un sesgo del modelo preentrenado, coherente con estudios que documentan estereotipos demográficos en SD (Bianchi et al., 2023; Luccioni et al., 2023), y lo tratamos como la limitación principal (sección 9).

<figure><img src="figuras/fig5_barrido.png" style="width:74%"><figcaption>Figura 6. Barrido de <i>strength</i> (0,45, 0,60 y 0,75) con el estilo Formal Clásico y la misma semilla.</figcaption></figure>

**Efecto del LoRA.** El adaptador funciona, pero su efecto es pequeño (Figura 7):

- **Detalle:** con el *strength* de los estilos (0,42 a 0,48), aumenta entre 0,7 % y 1,3 %. A 0,60 aumenta 4,9 % (de 97,7 a 102,5).
- **Diferencia de píxeles:** en promedio, 0,4 % a 0,7 % respecto de la imagen sin LoRA.
- **Latencia:** suma unos 0,3 s por imagen.
- **Identidad:** no cambia el compromiso entre ropa e identidad; el pelo se altera igual con y sin LoRA.

Es coherente con lo que es: un LoRA de detalle, usado con escala 0,6, que no aprendió un estilo corporativo.

<figure><img src="figuras/fig9_lora.png" style="width:64%"><figcaption>Figura 7. Estilo Formal Clásico con <i>strength</i> 0,60 y la misma semilla, sin LoRA y con LoRA.</figcaption></figure>

**Coherencia del agente.** Evaluamos el agente con 10 conjuntos de decisiones variadas sobre el paquete de 5 estilos:

| Agente | Corridas | Fidelidad media | Fidelidad mínima | Latencia media (máx.) |
|---|---|---|---|---|
| Gemini 3.5 Flash Lite | 10 | 100 % | 100 % | 11,9 s (19,9 s) |
| Agente de reglas | 10 | 100 % | 100 % | < 0,01 s |

La primera versión de la métrica daba 93,8 % a Gemini. Al revisar los cinco casos con 87,5 %, encontramos que no eran errores del modelo, sino falsos negativos de la métrica ante frases como "no fue aceptada a pesar de…". Corregimos el manejo de negaciones y comprobamos que la métrica sigue detectando errores reales: con polaridad invertida, títulos omitidos o conteos incorrectos da entre 50 % y 67 %. En todas las corridas, Gemini listó las cinco variaciones con su decisión correcta y justificó cada una con la iluminación, el fondo y los comentarios del usuario, sin inventar preferencias.

## 8. Iteraciones guiadas por las pruebas

| Prueba | Problema observado | Cambio realizado |
|---|---|---|
| Selfie muy cercana tomada desde abajo (foto A) | El detector facial no encontraba la cara | Reducción a 640 px, ecualización y dos clasificadores Haar |
| Misma foto | El recorte no cabía, quedaba rectangular y al escalarlo achataba la cara | Recorte siempre cuadrado, limitado por los bordes de la foto |
| Fotos de celular | La orientación EXIF no se aplicaba | Corrección de la orientación al subir la foto |
| Agente con Gemini | Gemini 2.5 Flash no está disponible para cuentas nuevas; los modelos grandes respondían 503 o no respondían | Cadena de modelos *lite* con reintentos: la latencia bajó de 68 s a 4–20 s |
| Conexión con Colab | Cortes esporádicos del túnel de Cloudflare | Reintento automático de la petición |
| Métrica de fidelidad | Falsos negativos con negaciones | Normalización de "no fue aceptada / rechazada" |
| Filtro ético | Dejaba pasar variantes como "s1n r0pa" o "shirtless" | Normalización de números usados como letras y términos nuevos |
| Primera corrida en Colab | El LoRA no cargó por el conflicto con `torchao` | Desinstalación de `torchao` en el notebook; en la segunda corrida el LoRA carga |

## 9. Limitaciones y trabajo futuro

1. **Identidad frente a vestimenta.** El img2img aplicado a toda la imagen obliga a elegir entre conservar la identidad (*strength* bajo) y cambiar la ropa (*strength* alto). La mejora propuesta es usar *inpainting* con una máscara facial, que conserva los píxeles reales de la cara y el pelo y regenera solo la ropa y el fondo (Lugmayr et al., 2022), con un *strength* de 0,75 o más.
2. **Influencia de los bordes Canny.** Los bordes fijan también el cuello de la polera original, lo que dificulta dibujar un cuello de camisa. Una alternativa es atenuar los bordes en la zona del torso.
3. **Alcance del LoRA.** El LoRA público mejora poco el detalle y no aporta un estilo de retrato corporativo. Un LoRA entrenado en Colab con retratos ejecutivos de licencia libre permitiría personalizar de verdad la vestimenta y la iluminación.
4. **Alcance de la métrica de fidelidad.** Supone que la explicación está organizada en secciones, con la decisión antes del título, que es el formato que se pide al modelo. No evalúa la calidad de las justificaciones.
5. **Infraestructura.** Las sesiones gratuitas de Colab expiran y el túnel cambia de URL en cada ejecución. Para la demostración se debe ejecutar el notebook poco antes.

## 10. Consideraciones éticas

**Manipulación de identidad.** Un sistema que modifica retratos puede usarse para suplantar a otra persona o para presentarse de forma engañosa. Lo limitamos de tres formas: el caso de uso es la propia foto del usuario, las variaciones son estilos profesionales acotados y la interfaz no ofrece edición libre de rasgos. Nuestros resultados muestran que el modelo puede alterar rasgos sin pedirlo. Por eso la interfaz deja la decisión final en manos del usuario y no publica nada de forma automática.

**Sesgo.** El cambio de textura del pelo y la filtración de colores del texto al pelo son sesgos heredados del preentrenamiento con datos web. Afectan más a personas cuyos rasgos están menos representados en esos datos. Lo reportamos en lugar de ocultarlo y la mejora de la sección 9 lo ataca directamente.

**Guardrails implementados:**

- Filtro léxico preventivo con normalización de tildes y de números usados como letras. Bloquea antes de usar la GPU y muestra la categoría de la infracción.
- El filtro de contenido de Stable Diffusion se mantiene activo y su resultado se registra en cada imagen.
- El prompt negativo excluye desnudez y deformaciones.

**Privacidad.** Las fotos y decisiones se guardan en `data/processed/`, excluida del repositorio por `.gitignore`. La clave de API se lee de un archivo `.env` que no se versiona. El código de participante es anónimo. Las fotos de este informe son de un integrante del equipo y se usan con su consentimiento.

**Propiedad intelectual.** SD 1.5 se distribuye bajo la licencia CreativeML OpenRAIL-M y ControlNet bajo OpenRAIL. Ambas permiten el uso con restricciones de uso responsable. El LoRA es de un tercero y se cita como tal. La autoría de imágenes generadas a partir de la foto de una persona y de un modelo entrenado con obras de terceros es una pregunta abierta que el usuario debe considerar antes de publicar.

## 11. Conclusiones

El sistema cumple el ciclo del enunciado de extremo a extremo:

- genera cinco variaciones por foto con dos métodos en una GPU gratuita;
- registra decisiones estructuradas por imagen;
- produce una explicación que lista explícitamente lo aceptado y lo rechazado, con 100 % de fidelidad medida en 10 corridas.

La evaluación cuantitativa mostró que el control de la ropa y la conservación de la identidad compiten cuando el img2img se aplica a toda la imagen. Este hallazgo, más que las cifras de latencia, es el aporte principal: indica que el siguiente paso es conservar la cara por máscara y no aumentar la intensidad del modelo.

<div class="bibliografia" markdown="1">

## Bibliografía

Amershi, S., Weld, D., Vorvoreanu, M., Fourney, A., Nushi, B., Collisson, P., ... y Horvitz, E. (2019). Guidelines for human-AI interaction. *Proceedings of the 2019 CHI Conference on Human Factors in Computing Systems*, 1–13.

Bianchi, F., Kalluri, P., Durmus, E., Ladhak, F., Cheng, M., Nozza, D., ... y Caliskan, A. (2023). Easily accessible text-to-image generation amplifies demographic stereotypes at large scale. *Proceedings of the 2023 ACM Conference on Fairness, Accountability, and Transparency*, 1493–1504.

Brown, T. (2008). Design thinking. *Harvard Business Review*, 86(6), 84–92.

Canny, J. (1986). A computational approach to edge detection. *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 8(6), 679–698.

Ho, J., Jain, A. y Abbeel, P. (2020). Denoising diffusion probabilistic models. *Advances in Neural Information Processing Systems*, 33, 6840–6851.

Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L. y Chen, W. (2022). LoRA: Low-rank adaptation of large language models. *International Conference on Learning Representations*.

Luccioni, A. S., Akiki, C., Mitchell, M. y Jernite, Y. (2023). Stable bias: Evaluating societal representations in diffusion models. *Advances in Neural Information Processing Systems*, 36 (Datasets and Benchmarks Track).

Lugmayr, A., Danelljan, M., Romero, A., Yu, F., Timofte, R. y Van Gool, L. (2022). RePaint: Inpainting using denoising diffusion probabilistic models. *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, 11461–11471.

Meng, C., He, Y., Song, Y., Song, J., Wu, J., Zhu, J.-Y. y Ermon, S. (2022). SDEdit: Guided image synthesis and editing with stochastic differential equations. *International Conference on Learning Representations*.

Rombach, R., Blattmann, A., Lorenz, D., Esser, P. y Ommer, B. (2022). High-resolution image synthesis with latent diffusion models. *Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition*, 10684–10695.

Schuhmann, C., Beaumont, R., Vencu, R., Gordon, C., Wightman, R., Cherti, M., ... y Jitsev, J. (2022). LAION-5B: An open large-scale dataset for training next generation image-text models. *Advances in Neural Information Processing Systems*, 35 (Datasets and Benchmarks Track).

Viola, P. y Jones, M. (2001). Rapid object detection using a boosted cascade of simple features. *Proceedings of the 2001 IEEE Computer Society Conference on Computer Vision and Pattern Recognition*, I-511–I-518.

Zhang, L., Rao, A. y Agrawala, M. (2023). Adding conditional control to text-to-image diffusion models. *Proceedings of the IEEE/CVF International Conference on Computer Vision*, 3836–3847.

Recursos de software: Hugging Face Diffusers y PEFT; Streamlit; FastAPI; OpenCV; API de Google Gemini; LoRA `OedoSoldier/detail-tweaker-lora` (Hugging Face).

</div>

<div class="anexos" markdown="1">

## Anexo A. Ejemplos de variaciones

<figure><img src="figuras/fig4_basico.png" style="width:100%"><figcaption>Figura A1. Nivel básico (SD 1.5 img2img sin ControlNet), con la misma foto y las mismas semillas que la Figura 5. Los resultados son muy parecidos a los del nivel intermedio con esta intensidad; también aquí el pelo cambia en "Smart Casual" y "WhatsApp Business Casual".</figcaption></figure>

**Catálogo de estilos.** El paquete evaluado es "Corporativo Multiplataforma", de 5 variaciones.

| Estilo | Red | Vestimenta (texto para el modelo, resumido) | *Strength* | *Guidance* |
|---|---|---|---|---|
| LinkedIn – Formal Clásico | LinkedIn | Navy blue business suit, white shirt, tie | 0,42 | 7,5 |
| LinkedIn – Business Casual | LinkedIn | Navy blazer, light blue open collar shirt | 0,45 | 7,5 |
| LinkedIn – Smart Casual | LinkedIn | Neat crew neck sweater | 0,48 | 7,0 |
| WhatsApp – Business Casual | WhatsApp | Casual blazer over a plain t-shirt | 0,43 | 7,2 |
| WhatsApp – Smart Casual Cercano | WhatsApp | Clean light polo shirt, bright daylight | 0,45 | 7,0 |
| LinkedIn – Black Tie | LinkedIn | Black tuxedo, bow tie | 0,40 | 8,0 |
| GitHub – Tech Casual | GitHub | Plain dark hoodie, monitors background | 0,46 | 7,5 |
| Redes – Creativo de Estudio | Redes | Modern tailored jacket, rim lighting | 0,50 | 8,0 |

Todos los textos terminan con "professional headshot photo, sharp focus on face, realistic skin, 85mm lens" y usan un prompt negativo que excluye deformaciones, ilustración, texto y desnudez.

## Anexo B. Filtro ético en la interfaz

<figure><img src="figuras/fig8_filtro.png" style="width:30%"><figcaption>Figura B1. El filtro ético bloquea "foto sin ropa" mientras se escribe, antes de generar. También bloquea variantes como "s1n r0pa", "sin camisa" o "shirtless".</figcaption></figure>

## Anexo C. Registro de decisiones y salida del agente

Registro real de la sesión de la Figura 3 (`user_decisions.json`, primera de cinco entradas):

<pre>{
  "variation_id": "gpu_var_linkedin_formal_55367",
  "preset_id": "linkedin_formal",
  "title": "LinkedIn - Formal Clásico",
  "platform": "LinkedIn",
  "formality": "Formal",
  "accepted": true,
  "rating": 4,
  "recommended_lighting": "Luz frontal difusa de tres puntos",
  "recommended_background": "Oficina corporativa moderna con bokeh suave",
  "user_notes": "Se ve serio, lo usaría en LinkedIn",
  "latency_seconds": 6.937,
  "engine_mode": "Nivel Intermedio (ControlNet Canny + img2img, GPU)"
}</pre>

Lista determinista generada a partir de ese registro (sección 6):

<pre>Resultado: 5 variaciones evaluadas, con una tasa de aprobación de 60.0%.
Variaciones aceptadas (3)
- LinkedIn - Formal Clásico (calificación 4/5) «Se ve serio, lo usaría en LinkedIn»
- LinkedIn - Smart Casual (calificación 4/5)
- WhatsApp - Business Casual (calificación 4/5) «Buena luz»
Variaciones rechazadas (2)
- LinkedIn - Business Casual (calificación 4/5) «El cuello de la polera no queda formal»
- WhatsApp - Smart Casual Cercano (calificación 4/5) «El pelo no se parece al mío»</pre>

En esta sesión de prueba no se movió el control de calificación, así que todas las variaciones quedaron con el valor inicial de 4.

## Anexo D. Reproducibilidad

1. **Servidor GPU.** Subir `notebooks/controlnet_portrait_pipeline.ipynb` a Google Colab, elegir GPU T4 y usar "Ejecutar todas". El notebook pide la foto, guarda los resultados en `resultados_colab.zip` y publica el servidor con una URL `trycloudflare.com`.
2. **Interfaz.** En `Project-II`, ejecutar `pip install -r requirements.txt` y luego `streamlit run ui/app.py` (o `run_app.bat`). Pegar la URL del servidor y presionar "Probar Conexión GPU".
3. **Agente con Gemini.** Crear un archivo `.env` con la línea `GEMINI_API_KEY=...`.
4. **Métricas.** Ejecutar `material_apoyo/informe/medir_imagenes.py` (métricas de imagen) y `material_apoyo/informe/evaluar_agente.py 10` (fidelidad del agente). Los resultados se guardan en `material_apoyo/informe/datos/`.

Versiones probadas: Python 3.10 en local y 3.13 en Colab; en local, Diffusers 0.41, Transformers 5.20, PEFT 0.21 y Streamlit 1.65.

</div>
