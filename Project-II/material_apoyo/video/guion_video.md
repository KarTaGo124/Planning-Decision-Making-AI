# Video demostrativo: guion y lista de control

**Duración máxima:** 3:00 (se pueden cortar las esperas al editar).
**Participante:** docente de la UTEC, o alumno de pregrado de una carrera que **no** sea Ciencia de la Computación ni Ciencia de Datos.
**Roles:**
- **Participante (P):** usa el sistema con su propia foto y decide.
- **Operador (O):** integrante del equipo. Maneja la computadora y habla fuera de cámara.

**Qué debe verse y oírse, según el enunciado y el profesor:**
1. La presentación de la persona y su consentimiento, en los primeros 10 segundos.
2. La generación de las **5** variaciones.
3. El Aceptar o Rechazar de **cada una**, con la voz de la persona diciendo qué elige y por qué.
4. El resumen automático del agente.
5. El comentario final de la persona.

---

## Antes de grabar (15 minutos)

1. En Colab, sube el notebook `Project-II/notebooks/controlnet_portrait_pipeline.ipynb`, elige **T4 GPU** y luego **Ejecutar todas**. Cuando lo pida, sube cualquier foto de prueba. Espera a que aparezca la URL `https://....trycloudflare.com` al final.
2. Revisa que la celda final diga `Servidor listo: Tesla T4 | LoRA: True`.
3. En la computadora, borra `Project-II/data/processed/user_decisions.json` si existe. Así el contador empieza en 0 y no se mezclan decisiones de pruebas anteriores.
4. Abre la app con `run_app.bat`.
5. En la barra lateral:
   1. Elige **Nivel Intermedio (ControlNet Canny + img2img, GPU)**.
   2. Pega la URL y presiona **Probar conexión**. Debe decir `Conectado a Tesla T4, LoRA activo`.
   3. Elige el **Paquete Corporativo Multiplataforma (5 Variaciones)**.
   4. En "Modelo para la explicación", elige **Google Gemini Flash (API)**.
6. Haz una corrida de prueba completa y después borra otra vez `user_decisions.json` y recarga la página (F5).
7. Pídele al participante una foto suya: de frente, a la altura de los ojos, de pecho hacia arriba, fondo liso y sin audífonos. Pásala a la computadora.
8. Prepara la grabación:
   - **Software:** OBS Studio, o `Win + Alt + R` (Xbox Game Bar).
   - **Calidad:** 1080p y micrófono probado.
   - **Pantalla:** el navegador en pantalla completa (F11) y las notificaciones cerradas.

---

## Guion

### 0:00 – 0:10 · Presentación y consentimiento (participante en cámara)

**P:**
> "Hola, soy **[nombre y apellido]**, estudiante de **[carrera]** de la UTEC *(o: docente de **[departamento]** de la UTEC)*. Acepto participar en esta grabación y que se use mi foto para el Proyecto 2 del curso Planificación y Toma de Decisiones en IA."

### 0:10 – 0:25 · Qué es el sistema (pantalla, voz del operador)

*Pantalla: la app abierta, con la barra lateral visible.*

**O:**
> "Este sistema genera cinco variaciones de una foto profesional para LinkedIn y WhatsApp corporativo. Corre en una GPU de Google Colab con Stable Diffusion y ControlNet. La persona acepta o rechaza cada variación y un agente de IA explica sus elecciones."

*Señala con el mouse `Conectado a Tesla T4, LoRA activo`.*

### 0:25 – 0:40 · Filtro ético (pantalla)

*El operador escribe en "Ajuste de vestimenta" el texto `sin ropa` y aparece el aviso rojo.*

**O:**
> "Antes de generar, un filtro bloquea pedidos no profesionales. Por ejemplo, 'sin ropa' se bloquea y nunca llega a la GPU."

*Borra el texto.*

### 0:40 – 1:00 · Carga de la foto y generación

*El participante, o el operador, sube la foto en "Foto (PNG o JPG)".*

**P:**
> "Subo una foto mía. Quiero una foto para mi perfil de LinkedIn."

*Clic en **Generar variaciones**. Al editar, corta la espera de unos 30 segundos y deja visible el mensaje "Se generaron 5 variaciones".*

**O:**
> "El paquete genera exactamente cinco variaciones. Todas empiezan en estado Pendiente."

### 1:00 – 2:10 · Decisión sobre cada variación (pantalla, voz del participante)

*Baja por las cinco tarjetas. En cada una, el participante mira la imagen, dice su decisión, mueve la calificación y escribe un comentario corto. Las decisiones y los motivos son **de la persona**; no los dictes. Puede usar este formato:*

**P, en cada una:**
> "La número **[1]**, **[nombre del estilo]**: la **[acepto / rechazo]** porque **[motivo: me reconozco / no me reconozco, la ropa se ve formal / informal, la luz, el fondo]**. Le pongo **[1 a 5]**."

*Ejemplos de motivos que suelen aparecer: "se ve serio", "el cuello no queda formal", "el pelo no se parece al mío", "buena luz", "el fondo se ve falso".*

*Después de las cinco, el operador señala las etiquetas "Aceptada / Rechazada".*

**O:**
> "Cada clic queda registrado con la calificación y el comentario en un archivo JSON."

### 2:10 – 2:40 · Resumen del agente

*Clic en **Generar explicación**. Al editar, corta la espera, que es de unos 10 segundos.*

**O:**
> "El agente, con Gemini, lista qué variaciones se aceptaron y cuáles se rechazaron, y explica por qué, usando solo los datos registrados. La fidelidad con el registro aparece arriba."

*Baja despacio por "Variaciones aceptadas" y "Variaciones rechazadas" para que se lean.*

**P:**
> "Sí, coincide con lo que elegí: acepté **[n]** y rechacé **[n]**."

### 2:40 – 3:00 · Comentario final (participante, en cámara o en voz)

**P (opinión propia, unos 15 segundos):**
> "**[¿Usarías alguna de estas fotos? ¿Cuál y por qué? ¿Qué mejorarías?]**"

**O:**
> "Gracias. Este fue el Proyecto 2 del Grupo 7."

---

## Después de grabar

1. Edita y corta las esperas. Revisa que dure **3:00 o menos**.
2. Revisa que se vean y se oigan:
   - la presentación y el consentimiento al inicio;
   - las 5 variaciones;
   - el Aceptar o Rechazar de cada una, con su motivo en voz;
   - el resumen del agente;
   - el comentario final.
3. Súbelo a YouTube como **No listado**, o a Drive con "Cualquier persona con el enlace".
4. Pega el link en `entregable/ENTREGA.txt`.
5. Guarda la sesión: escribe el código del participante en la barra lateral y presiona **Guardar y cerrar sesión**. El archivo queda en `data/processed/sessions/`.
