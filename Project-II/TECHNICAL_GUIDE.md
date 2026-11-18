# Guía técnica: sistema generativo de retratos profesionales

CS5363 Planificación y Toma de Decisiones en IA (UTEC 2026-2) · Grupo 7

Esta guía describe el código. El análisis de resultados, las limitaciones y la reflexión ética están en el informe ([`material_apoyo/informe/informe.md`](material_apoyo/informe/informe.md)).

## 1. Flujo

```
foto + paquete de 5 estilos + prompt libre
  → safety.py       filtro ético (bloquea antes de la GPU)
  → generator.py    rotación EXIF, detección facial, recorte cuadrado 512 px, bordes Canny
  → gpu_server.py   FastAPI en Colab (T4) → diffusion.py
                      Nivel Intermedio: SD 1.5 + ControlNet Canny (img2img)
                      Nivel Básico:     SD 1.5 img2img sin ControlNet
                      LoRA público detail-tweaker (escala 0,6)
  → ui/app.py       5 variaciones en estado Pendiente; Aceptar/Rechazar, calificación, comentario
                      → data/processed/user_decisions.json, generated/, sessions/
  → agent.py        lista determinista de aceptadas/rechazadas + explicación con Gemini
  → evaluator.py    fidelidad de la explicación, aceptación, calificación, diversidad
```

## 2. Módulos (`src/`)

| Módulo | Responsabilidad |
|---|---|
| `config.py` | 8 estilos (red, formalidad, iluminación, fondo, vestimenta, *guidance*, *strength*) y 3 paquetes: dos de 5 variaciones y uno de 7. |
| `safety.py` | Normaliza el texto (NFKD, minúsculas y números usados como letras) y lo compara con una lista de términos y expresiones regulares por categoría: desnudez, ropa inapropiada, contenido explícito, violencia, sustancias y odio. |
| `generator.py` | `GenerationEngine`: preproceso y cliente HTTP del servidor GPU, con un reintento ante cortes. Incluye el modo de contingencia local, que solo aplica filtros OpenCV y no es generativo. |
| `diffusion.py` | `DiffusionEngine`: carga SD 1.5 y ControlNet Canny, construye la canalización img2img compartiendo componentes, carga y activa el LoRA, y define los prompts en inglés por estilo. |
| `gpu_server.py` | API FastAPI: `GET /health` y `POST /generate`. Los modelos se cargan al iniciar el servidor. |
| `agent.py` | `ExplanationAgent`: agente de reglas, Gemini (con cadena de modelos de respaldo y reintentos) y OpenAI. Lee las claves de `.env`. |
| `evaluator.py` | Métrica de fidelidad, que maneja negaciones; tasa de aceptación; calificación media; entropía de formalidades; latencia. |

## 3. API del servidor GPU

`POST /generate`

```json
{
  "image_base64": "<PNG 512x512>",
  "preset_ids": ["linkedin_formal", "..."],
  "custom_prompt": "corbata verde",
  "method": "controlnet_img2img | img2img",
  "num_steps": 25,
  "guidance_scale": null,
  "strength": null,
  "seed": null,
  "use_lora": true
}
```

Si `guidance_scale` o `strength` vienen en `null`, se usan los valores del estilo. La semilla por defecto es 1234 más el índice de la variación.

Códigos de respuesta:
- **400:** el prompt fue bloqueado, el método no existe o la imagen no es válida.
- **503:** los modelos no cargaron.
- **500:** la generación falló.

Cada variación devuelve la imagen, el prompt, los parámetros, si el LoRA estaba activo, si el filtro de SD la marcó y el tiempo de generación.

`GET /health` devuelve el dispositivo, si los modelos y el LoRA cargaron (con el error, si lo hubo) y los métodos disponibles.

## 4. Parámetros

- **Modelos:**
  - Base: `stable-diffusion-v1-5/stable-diffusion-v1-5`.
  - ControlNet: `lllyasviel/control_v11p_sd15_canny`, con escala de condicionamiento 0,85.
  - LoRA: `OedoSoldier/detail-tweaker-lora` (`add_detail.safetensors`, escala 0,6).
- **Generación:** 512 × 512 px, planificador UniPC con 25 pasos, *guidance* de 7,0 a 8,0 y *strength* de 0,40 a 0,50 según el estilo.
- **Bordes:** Canny con umbrales 100 y 200, tras un suavizado gaussiano de 3 × 3.
- **Detección facial:** dos clasificadores Haar (`alt2` y `default`) sobre la imagen reducida a 640 px y ecualizada. El recorte mide 1,9 veces el tamaño de la cara, es siempre cuadrado y nunca corta la parte superior de la cabeza.
- **Agente:** usa `gemini-3.5-flash-lite` y, como respaldo, `gemini-3.1-flash-lite`, `gemini-flash-lite-latest` y `gemini-3.8-flash`. Hace 2 intentos por modelo ante errores 429 o 5xx, con un tiempo límite de 25 s. El modelo se puede cambiar con `GEMINI_MODEL`.

## 5. Datos generados

Todo se guarda en `data/processed/`, que está excluida del repositorio:

| Ruta | Contenido |
|---|---|
| `user_decisions.json` | Decisiones de la sesión actual, una entrada por variación. |
| `generated/<fecha_hora>/` | Entrada, bordes Canny, las 5 imágenes y `batch.json` con el motor y los tiempos. |
| `sessions/<código>_<fecha>.json` | Sesión cerrada de un participante: perfil, métricas, explicación del agente y decisiones. |

## 6. Problemas conocidos

- **Torchao en Colab:** la versión 0.10 preinstalada impide cargar el LoRA con `peft`. El notebook la desinstala.
- **Túnel de Cloudflare:** la URL cambia en cada ejecución del notebook y las sesiones gratuitas de Colab expiran.
- **Identidad:** con *strength* de 0,60 o más aparece la ropa formal, pero cambian rasgos como la textura del pelo. La mejora propuesta es *inpainting* con máscara facial (sección 9 del informe).

La ejecución paso a paso está en [`HOW_TO_RUN.md`](HOW_TO_RUN.md).
