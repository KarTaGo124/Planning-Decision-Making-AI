# Guion de exposición · Proyecto 2 · Grupo 7

Retratos profesionales con IA, decididos por el usuario. CS5363 Planificación y Toma de Decisiones en IA, UTEC 2026-2.

Duración total: 18:10 (exposición 14:40 y demo en vivo 3:30), dentro de los 15 a 20 minutos. Después vienen 10 minutos de preguntas del jurado.

Quién habla: José (diapositivas 1 a 4 y 13), Matías (5 a 9 y 14, y opera la demo), Alejandro (10 a 12 y 15). El texto de cada bloque está también en las notas del orador de la presentación.

## Bloques y tiempos

| # | Diapositiva | Habla | Tiempo | Acumulado |
|---|---|---|---|---|
| 1 | Retratos profesionales con IA, decididos por el usuario | José | 0:45 | 0:45 |
| 2 | Un retrato profesional sigue siendo caro o poco fiable | José | 1:00 | 1:45 |
| 3 | Design Thinking: del reto a la propuesta de valor | José | 1:00 | 2:45 |
| 4 | Journey map: el usuario decide en cada paso | José | 0:55 | 3:40 |
| 5 | Arquitectura: de la foto a la explicación | Matías | 1:15 | 4:55 |
| 6 | Preprocesamiento: detectar, recortar y describir | Matías | 1:00 | 5:55 |
| 7 | Dos formas de generar sobre una GPU T4 | Matías | 1:30 | 7:25 |
| 8 | Interfaz: cada imagen espera la decisión humana | Matías | 0:45 | 8:10 |
| 9 | Demo en vivo | Matías | 3:30 | 11:40 |
| 10 | Resultados: 5 variaciones por foto en segundos | Alejandro | 1:00 | 12:40 |
| 11 | Hallazgo: más cambio de ropa, menos identidad | Alejandro | 1:25 | 14:05 |
| 12 | Agente explicador: fiel a las decisiones | Alejandro | 1:15 | 15:20 |
| 13 | Ética: guardrails antes, durante y después | José | 1:05 | 16:25 |
| 14 | Iteraciones guiadas por pruebas | Matías | 0:45 | 17:10 |
| 15 | Conclusiones y próximos pasos | Alejandro | 1:00 | 18:10 |

## Texto para leer

### 1. Retratos profesionales con IA, decididos por el usuario · José · 0:45

Buenos días. Somos el Grupo 7: Matías Meneses, Alejandro Ore y yo, José Gálvez. Les presentamos un sistema que genera retratos profesionales a partir de una foto cotidiana. La idea central es que la inteligencia artificial propone y la persona decide: el sistema genera cinco variaciones, el usuario acepta o rechaza cada una, y un agente basado en un modelo de lenguaje explica esas decisiones. En la imagen ven una foto de entrada y dos variaciones generadas en una GPU de Google Colab.

### 2. Un retrato profesional sigue siendo caro o poco fiable · José · 1:00

Empecemos por el problema. Una foto profesional de estudio cuesta, en promedio, entre 50 y 150 dólares, sin contar traslados ni postproducción, y para un estudiante es un gasto difícil. La alternativa obvia son los generadores de imágenes, pero tienen tres problemas. Primero, no preservan la identidad: la persona del resultado puede no parecerse a la de la foto. Segundo, no distinguen contexto: no es lo mismo una foto para LinkedIn formal que para un WhatsApp corporativo o para GitHub. Y tercero, no son transparentes: el usuario no sabe por qué el sistema le propone cada opción. Nuestra respuesta es generar cinco variaciones por foto, dejar que la persona elija y explicar sus elecciones.

### 3. Design Thinking: del reto a la propuesta de valor · José · 1:00

Para llegar a la propuesta seguimos el taller de Design Thinking de la semana 13. Formulamos la pregunta guía que ven arriba: cómo facilitar la generación accesible y controlada de retratos profesionales para estudiantes y jóvenes egresados. El perfil de usuario es un estudiante de ciclos avanzados o un egresado reciente, con poco presupuesto, que teme que la IA le deforme la cara y que necesita una foto distinta para cada red. La propuesta de valor tiene tres dimensiones: funcional, porque adapta el retrato a cada red con presets y un prompt libre; social, porque proyecta una imagen creíble ante reclutadores y clientes; y emocional, porque la persona siempre tiene la última palabra.

### 4. Journey map: el usuario decide en cada paso · José · 0:55

Este es el recorrido del usuario, en cinco pasos. Sube una selfie y elige un paquete de cinco estilos. Luego ve el recorte de su cara y los bordes que usará el modelo, para que entienda qué se conserva. Recibe cinco variaciones, todas en estado Pendiente. Acepta o rechaza cada una, le pone una calificación y, si quiere, un comentario. Y al final el agente le resume qué aceptó, qué rechazó y por qué. El estado Pendiente es importante: nada se da por aceptado hasta que la persona vota. Ahora Matías les explica cómo está construido.

### 5. Arquitectura: de la foto a la explicación · Matías · 1:15

Gracias, José. La arquitectura tiene ocho etapas. Arriba, la entrada: la foto, el paquete de estilos y un prompt libre opcional. Antes de usar la GPU pasa por un filtro ético que bloquea pedidos inapropiados. Después viene el preprocesamiento: detectamos la cara, la recortamos a 512 por 512 y extraemos sus bordes. La imagen viaja codificada en base64 a un servidor FastAPI en Google Colab, con una GPU Tesla T4, que genera las cinco variaciones. Abajo, las imágenes vuelven a la interfaz en Streamlit, donde la persona decide. Cada decisión se registra en un archivo JSON, y el agente explicador lo lee para producir el resumen y medir su propia fidelidad contra esos datos.

### 6. Preprocesamiento: detectar, recortar y describir · Matías · 1:00

El preprocesamiento es más importante de lo que parece. Usamos dos detectores de rostro Haar de OpenCV, recortamos un cuadrado de 512 píxeles centrado en la cara y extraemos los bordes con Canny, con umbrales 100 y 200. Esos bordes son los que ControlNet intenta respetar. Esto lo corregimos gracias a las pruebas: con una selfie muy cercana y tomada desde abajo, el detector no encontraba la cara, y cuando la encontraba, el recorte no cabía y la cara salía achatada. Ahora reducimos la imagen y ecualizamos el contraste antes de detectar, el recorte siempre es cuadrado y corregimos la rotación de las fotos de celular.

### 7. Dos formas de generar sobre una GPU T4 · Matías · 1:30

Implementamos dos formas de generar, como pide el enunciado. El nivel intermedio usa Stable Diffusion 1.5 con ControlNet Canny en modo img2img: los bordes de la cara condicionan la imagen con una escala de 0,85. El nivel básico usa el mismo modelo en img2img, pero sin ControlNet. En la GPU T4, el intermedio tarda 2,61 segundos por imagen y el básico 1,96. Si no hay GPU, la app tiene un respaldo con filtros de OpenCV, que no es generativo, solo para que la interfaz siga funcionando. Sobre personalización: usamos un LoRA público, detail-tweaker, con escala 0,6. El LoRA está integrado, pero en la corrida final no cargó por un conflicto de versiones de torchao en Colab: Colab trae la versión 0.10 y la librería peft exige una mayor a 0.16. El notebook ahora la desinstala, y verificamos localmente que el LoRA carga sobre la arquitectura de Stable Diffusion 1.5: 384 capas en la UNet y 144 en el codificador de texto. Los resultados que les mostraremos son sin LoRA.

### 8. Interfaz: cada imagen espera la decisión humana · Matías · 0:45

La interfaz está pensada para que la decisión sea siempre humana. Cada imagen empieza en estado Pendiente. Debajo tiene los botones Aceptar y Rechazar, una calificación de 1 a 5 y un campo de comentario. Todo se guarda al instante en un archivo JSON que se puede descargar, y cada sesión se guarda por participante. Hay ocho estilos, agrupados en tres paquetes, y un prompt libre para pedir detalles como el color de la corbata. Ahora lo vemos funcionando.

### 9. Demo en vivo · Matías · 3:30

Vamos a la demo. [Seguir los pasos de la sección «Demo en vivo» del guion.] Mientras se generan las imágenes: la app manda la foto al servidor de Colab; cada imagen tarda entre dos y tres segundos en la GPU, y con la red el lote completo toma de 25 a 35 segundos. [Votar las cinco en voz alta, diciendo por qué se acepta o se rechaza cada una.] [Pedir la explicación con Gemini y leer la lista de aceptadas y rechazadas, y la fidelidad.] [Escribir «sin ropa» en el prompt libre y mostrar el bloqueo.] Eso es el sistema completo. Alejandro les cuenta qué encontramos al evaluarlo.

### 10. Resultados: 5 variaciones por foto en segundos · Alejandro · 1:00

Gracias, Matías. Estos son resultados reales de la GPU, con la misma foto y las mismas semillas para los dos métodos. Arriba, el nivel intermedio con ControlNet; abajo, el básico. En la GPU cada imagen tarda 2,61 y 1,96 segundos, respectivamente. Desde la app, el lote de cinco toma de 25 a 35 segundos, entre 5 y 7 segundos por imagen, porque incluye la red por el túnel de Cloudflare. El filtro de contenido de Stable Diffusion no marcó ninguna imagen. Pero si miran la ropa, casi no cambia: la polera sigue ahí en casi todas. Eso nos llevó al hallazgo principal.

### 11. Hallazgo: más cambio de ropa, menos identidad · Alejandro · 1:25

Probamos tres valores de strength, que controla cuánto puede cambiar el modelo. Con los valores que usamos por defecto, entre 0,42 y 0,48, la ropa casi no cambia: la diferencia media entre pares de imágenes es de apenas 0,036 a 0,040 en una escala de cero a uno. Con 0,60 o más aparece el terno, pero la identidad se degrada: el pelo pasa de liso a ondulado o crespo, algo que también vimos en dos de las cinco variaciones. Además, en el estilo Formal Clásico el color navy blue del terno se filtra al pelo. Medimos el tono de piel y el cambio es pequeño: menos 0,4 de luminosidad en el centro de la cara y hasta menos 2,2 en la cara completa. Es un sesgo que hay que discutir: el modelo empuja rasgos hacia los patrones de sus datos de entrenamiento. La mejora que proponemos es inpainting con una máscara facial: conservar los píxeles de la cara y el pelo, y regenerar solo la ropa y el fondo.

### 12. Agente explicador: fiel a las decisiones · Alejandro · 1:15

El agente explicador usa Gemini 3.5 Flash Lite. Si ese modelo está saturado, prueba otros tres en cadena, y si todo falla usa un agente de reglas que funciona sin internet. Para controlar alucinaciones, la app siempre muestra primero la lista exacta de aceptadas y rechazadas, tomada del JSON, y después la explicación del modelo. Además medimos la fidelidad: revisamos que cada título aparezca con su decisión correcta y que los conteos coincidan. En diez corridas con decisiones distintas, Gemini obtuvo 100% en las diez, igual que el agente de reglas, con una latencia media de 11,9 segundos. Una aclaración honesta: la primera versión de la métrica daba 93,8%, pero eran falsos negativos de la métrica cuando el modelo escribía frases como «no fue aceptada»; la corregimos. Su límite es que supone una respuesta ordenada por secciones.

### 13. Ética: guardrails antes, durante y después · José · 1:05

En ética trabajamos en tres momentos. Antes de generar, un filtro bloquea términos de desnudez, violencia o contenido no profesional; normaliza tildes y números usados como letras, así que «s1n r0pa» también se bloquea, y lo hace antes de usar la GPU. Al generar, dejamos activo el filtro de contenido de Stable Diffusion. Y con los datos: las fotos y decisiones quedan fuera del repositorio, la clave de la API está en un archivo que no se versiona, y el sistema está pensado para usarse solo con la propia foto y con consentimiento. Los riesgos principales son la suplantación de identidad y el sesgo del modelo. Sobre propiedad intelectual, Stable Diffusion 1.5 y ControlNet tienen licencias OpenRAIL, que permiten su uso con restricciones de uso responsable.

### 14. Iteraciones guiadas por pruebas · Matías · 0:45

Esta tabla resume cómo las pruebas guiaron el desarrollo. Cada fila es un problema que encontramos usando el sistema y el cambio que hicimos: desde la detección de la cara y el recorte, hasta la cadena de modelos de Gemini, que bajó la espera de 68 segundos a entre 4 y 12, el reintento ante cortes del túnel, la métrica de fidelidad, el filtro ético y el conflicto de versiones que impidió cargar el LoRA.

### 15. Conclusiones y próximos pasos · Alejandro · 1:00

Para cerrar. Logramos un sistema completo: dos formas de generar en GPU con cinco variaciones por foto, una interfaz donde la persona decide imagen por imagen con un registro estructurado, un agente con 100% de fidelidad en nuestras pruebas y guardrails éticos. También encontramos su límite principal: con Stable Diffusion 1.5 en img2img, cambiar la ropa y conservar la identidad están en tensión. Los próximos pasos son el inpainting con máscara facial, confirmar el LoRA en la próxima corrida de Colab y evaluar también la calidad de las razones que da el agente. El código está en el repositorio que ven en pantalla. Muchas gracias; quedamos atentos a sus preguntas.

## Demo en vivo: pasos exactos

Preparación, 15 a 20 minutos antes de exponer (la primera vez Colab descarga unos 5 GB de modelos):

1. Abrir https://colab.research.google.com, ir a **Archivo, Subir notebook** y elegir `Project-II/notebooks/controlnet_portrait_pipeline.ipynb`.
2. **Entorno de ejecución, Cambiar tipo de entorno de ejecución, T4 GPU**, Guardar.
3. **Entorno de ejecución, Ejecutar todas**. Cuando la sección 4 lo pida, subir la foto.
4. Esperar la sección 9 y copiar la URL que termina en `.trycloudflare.com`. No cerrar la pestaña de Colab: esa celda queda corriendo.
5. Revisar que exista el archivo `.env` con `GEMINI_API_KEY` en la raíz del repositorio de la laptop de la demo.
6. En la laptop, doble clic en `Project-II/run_app.bat`. Se abre http://localhost:8501.
7. En la barra lateral, en **Motor generativo**, elegir **Nivel Intermedio (ControlNet Canny + img2img, GPU)**. Pegar la URL y presionar **Probar Conexión GPU**. Debe aparecer `Conectado: Tesla T4` (si dice `LoRA no cargado`, seguir: está explicado en la diapositiva 7).

Durante la demo (unos 3 minutos y medio):

1. En **1. Fotografía de Entrada**, subir la foto.
2. En **Seleccione un paquete sugerido**, dejar **Paquete Corporativo Multiplataforma (5 Variaciones)**.
3. Presionar **Generar Variaciones Visuales**. Tarda de 25 a 35 s; mientras tanto, explicar que la foto viaja al servidor de Colab.
4. Votar las 5 variaciones con **Aceptar** o **Rechazar**, mover la calificación y escribir un comentario corto en una o dos. Decir en voz alta por qué.
5. En **Modelo para Sintetizar Explicaciones**, elegir **Google Gemini Flash (API)** y presionar **Generar Explicación con Agente IA**. Leer la lista de aceptadas y rechazadas y la fidelidad.
6. En **Personalización (Prompt Libre)**, escribir `sin ropa` y presionar Enter. Mostrar el bloqueo en rojo.

Si una generación falla con «Remote end closed connection», es un corte del túnel: presionar de nuevo **Generar Variaciones Visuales**.

## Plan B si falla la GPU

1. Elegir **Contingencia local (filtro OpenCV, sin modelo generativo)** y decirlo explícitamente: ese modo no es generativo, pero el flujo de decisión, el registro en JSON, el agente y el filtro ético funcionan igual.
2. Mostrar las imágenes reales ya generadas en Colab: diapositivas 10 y 11, y la carpeta `Project-II/data/processed/colab_v1_img2img_sin_preservacion/` (archivos `resumen_*.png`).
3. Si Gemini no responde, el agente usa otro modelo de la cadena o el agente de reglas, que funciona sin internet. La app muestra el motivo en «Modelo Utilizado».

## Preguntas probables del jurado

**1. ¿Por qué Stable Diffusion 1.5 y no un modelo más nuevo?**
Porque corre con ControlNet y LoRA dentro de la GPU T4 gratuita de Colab, con 2 a 3 s por imagen, y su ecosistema está maduro. Modelos más grandes superan la memoria o el tiempo disponibles gratis.

**2. ¿El sistema preserva la identidad?**
No del todo. Con strength bajo la ropa casi no cambia y, aun así, el pelo cambió de textura en 2 de 5 variaciones; con 0,60 o más aparece el terno y el cambio de identidad es mayor. Lo medimos y lo presentamos como la limitación principal. La mejora es inpainting con máscara facial.

**3. ¿Qué aporta ControlNet si el nivel básico se parece tanto?**
Con strength entre 0,42 y 0,48 ambos dependen sobre todo de la foto inicial, así que las diferencias fueron pequeñas. ControlNet está pensado para fijar la estructura de la cara cuando se sube el strength, pero no comparamos los dos métodos con strength alto: es una prueba pendiente. Cuesta 0,65 s más por imagen.

**4. ¿Por qué no entrenaron un LoRA propio?**
Por tiempo y por las restricciones de acceso a Khipu. Usamos un LoRA público. El LoRA está integrado, pero en la corrida final no cargó por un conflicto de versiones de torchao en Colab; el notebook ya lo corrige y verificamos localmente que carga.

**5. ¿Cómo saben que el agente no inventa decisiones?**
La app muestra primero la lista exacta de aceptadas y rechazadas, tomada del JSON, y aparte medimos la fidelidad de la explicación del modelo: 100% en 10 corridas. La métrica no evalúa si las razones son buenas, solo que sean consistentes con los datos, y supone una respuesta ordenada por secciones.

**6. ¿Qué pasa si Gemini no responde?**
El agente prueba otros tres modelos en cadena y, si ninguno responde, usa el agente de reglas, que funciona sin internet. La demo no depende de que Gemini esté disponible.

**7. ¿Se puede engañar al filtro ético?**
Es un filtro léxico: cubre tildes, mayúsculas y números usados como letras, pero no entiende paráfrasis elaboradas. Por eso hay una segunda capa, el filtro de contenido de Stable Diffusion, que está activo.

**8. ¿Qué datos guardan y dónde?**
Las decisiones, sesiones e imágenes quedan en `data/processed`, que está fuera del repositorio. La foto se envía al servidor de Colab del propio equipo y no se publica. La API key está en un `.env` que no se versiona.

**9. ¿Usaron un dataset de rostros?**
No entrenamos un modelo: usamos modelos preentrenados, y la entrada es la foto de la persona. El sesgo que observamos viene de los datos con que se entrenó Stable Diffusion (LAION). Las pruebas se hicieron con fotos del equipo, con consentimiento.

**10. ¿De quién es la propiedad intelectual de las imágenes generadas?**
Stable Diffusion 1.5 (CreativeML OpenRAIL-M) y ControlNet (OpenRAIL) permiten el uso de las imágenes con restricciones de uso responsable. La foto de entrada es de la propia persona y no usamos fotos de terceros.
