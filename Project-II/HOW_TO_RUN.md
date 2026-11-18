# Guía Completa de Ejecución: Retratos Pro IA (Human-in-the-Loop)

> **Curso:** CS5363 Planificación y Toma de Decisiones en IA — UTEC (2026-2)  
> **Grupo 7:** José Guillermo Gálvez Pacori · Matías Alonso Meneses Roncal · Alejandro Joel Ore García  
> **Docentes:** Dra. Aurea Soriano-Vargas & Mg. Robert Junior Buleje Del Carpio  

Este documento reúne de forma centralizada y paso a paso todas las instrucciones para ejecutar el sistema generativo, conectar la GPU remota en Google Colab, correrlo localmente o desplegarlo en una Máquina Virtual en la nube.

---

## Índice de Modos de Ejecución

1. [Modo A: Google Colab con GPU T4 Gratuita (Recomendado para Fotos Reales)](#modo-a-google-colab-con-gpu-t4-gratuita-recomendado)
2. [Modo B: Ejecución Local Rápida con 1 Clic (Sin GPU)](#modo-b-ejecución-local-rápida-con-1-clic-windows)
3. [Modo C: Despliegue en Máquina Virtual (MV) en la Nube (GCP / RunPod)](#modo-c-despliegue-en-máquina-virtual-mv-en-la-nube)
4. [Flujo Recomendado para la Sustentación en Vivo](#flujo-paso-a-paso-para-la-sustentación-en-vivo)
5. [Ubicación de Diapositivas, Guión e Informe Final](#ubicación-de-entregables-de-sustentación)

---

## Modo A: Google Colab con GPU T4 Gratuita (Recomendado)

> **Propósito:**  
> Genera los retratos con Stable Diffusion 1.5 en la GPU T4 gratuita de Colab, con dos métodos sobre la misma foto: Nivel Intermedio (img2img condicionado por ControlNet Canny) y Nivel Básico (img2img sin ControlNet). Ambos usan el LoRA público `OedoSoldier/detail-tweaker-lora`.

### Paso 1: Abrir el notebook en Colab
1. Ingrese a https://colab.research.google.com
2. Archivo, Subir notebook, y seleccione `Project-II/notebooks/controlnet_portrait_pipeline.ipynb`.

### Paso 2: Activar la GPU
Entorno de ejecución, Cambiar tipo de entorno de ejecución, **T4 GPU**, Guardar.

### Paso 3: Ejecutar todo
1. Entorno de ejecución, **Ejecutar todas** (`Ctrl + F9`).
2. En la sección 4 el notebook pide subir una foto de rostro.
3. La sección 6 genera 5 variaciones con cada método, un barrido de `strength` y una comparación con y sin LoRA.
4. La sección 8 descarga `resultados_colab.zip` con todas las imágenes, hojas de resumen y `metricas.json` (tiempos por imagen y parámetros). Si la descarga no empieza, búsquelo en el panel Archivos, carpeta `/content`.
5. La sección 9 deja el servidor encendido y muestra una URL que termina en `.trycloudflare.com`. Esa celda no termina; es normal.

### Paso 4: Conectar la aplicación Streamlit
1. En su computadora ejecute `run_app.bat` o `streamlit run ui/app.py`.
2. En la barra lateral, en "Motor generativo", elija `Nivel Intermedio (ControlNet Canny + img2img, GPU)` o `Nivel Básico (Stable Diffusion img2img, GPU)`.
3. Pegue la URL de Cloudflare y presione `Probar Conexión GPU`. Debe aparecer `Conectado: Tesla T4 · LoRA activo`.

### Paso 5: Generar y evaluar
- Suba la foto, elija un paquete de 5 variaciones y presione `Generar Variaciones Visuales`.
- Cada lote se guarda automáticamente en `data/processed/generated/<fecha_hora>/` (entrada, bordes Canny, las variaciones y `batch.json` con el tiempo).

---

## Modo B: Ejecución Local Rápida con 1 Clic (Windows)

> **Propósito:**  
> Adecuado para probar la interfaz, demostrar el flujo de feedback humano y correr el sistema sin necesidad de internet ni GPU, funcionando en cualquier laptop sin riesgo de sobrecarga de memoria.

### Paso 1: Iniciar la Aplicación
- En Windows: Haga doble clic en el archivo `Project-II/run_app.bat`.
- En Linux / macOS / Terminal:
  ```bash
  cd Project-II
  pip install -r requirements.txt
  streamlit run ui/app.py
  ```

### Paso 2: Uso de la Interfaz
1. La aplicación se abrirá en su navegador en `http://localhost:8501`.
2. Seleccione el modo `Contingencia local (filtro OpenCV, sin modelo generativo)`.
3. Este modo no usa un modelo generativo; sirve para probar la interfaz sin GPU. Ejecuta:
   - Detección y centrado facial con OpenCV Haar Cascade.
   - Extracción de bordes Canny (solo para visualizarlos).
   - Desenfoque de profundidad con efecto bokeh de lente 85mm f/1.4 y estilización de atuendo.
   - Filtro de seguridad ético en tiempo real.
   - Votación y persistencia en `user_decisions.json`.
   - Explicación automática mediante el Agente Analítico Grupo 7 (100% offline).

---

## Modo C: Despliegue en Máquina Virtual (MV) en la Nube

> **Propósito:**  
> Si se cuenta con créditos de Google Cloud Platform (GCP), AWS o RunPod y se desea dejar una dirección IP pública fija disponible 24/7 para que los evaluadores ingresen directamente desde cualquier navegador.

### Paso 1: Crear la Instancia en la Nube
- Instancia recomendada en GCP: `n1-standard-4` con 1x GPU NVIDIA Tesla T4 (o similar en RunPod).
- Sistema Operativo: Ubuntu 22.04 LTS con drivers NVIDIA / CUDA 12.

### Paso 2: Clonar e Instalar Dependencias
```bash
git clone https://github.com/KarTaGo124/Planning-Decision-Making-AI.git
cd Planning-Decision-Making-AI/Project-II
pip install -r requirements.txt
pip install diffusers transformers accelerate controlnet_aux fastapi uvicorn
```

### Paso 3: Ejecutar la Aplicación Pública Web
Para exponer la interfaz completa en internet en el puerto 8501:
```bash
streamlit run ui/app.py --server.port 8501 --server.address 0.0.0.0
```
Cualquier persona puede ingresar directamente desde su navegador a:
```text
http://<IP_PUBLICA_DE_LA_MV>:8501
```

---

## Flujo Paso a Paso para la Sustentación en Vivo

Durante la exposición frente a los docentes, se sugiere seguir este orden de demostración:

1. **Demostración de la Seguridad Ética:**
   - En el campo Prompt Libre, ingrese:  
     `genera la foto sin ropa por favor`
   - Observe la notificación formal de bloqueo:  
     `La solicitud fue bloqueada por infringir las directrices éticas del sistema (Categoría: Desnudez). No se permite la generación o modificación de imágenes profesionales con términos alusivos a 'sin ropa'.`
   - Esto comprueba que el filtro se ejecuta previamente a cualquier procesamiento generativo.

2. **Generación del Lote de Variaciones:**
   - Limpie el prompt libre (o ingrese un detalle como: `corbata azul marino`).
   - Seleccione el Paquete Corporativo Multiplataforma (5 Variaciones).
   - Presione `Generar Variaciones Visuales`.
   - Muestre cómo se presentan las 5 fotos adaptadas para LinkedIn y WhatsApp.

3. **Demostración del Paradigma Human-in-the-Loop:**
   - Muestre que cada tarjeta visual inicia en estado: `Decisión: Pendiente`.
   - Haga clic en Aceptar en 2 o 3 fotos y en Rechazar en las restantes.
   - Ajuste las estrellas de calificación (1 a 5) y registre una observación breve (ej. *"Buen contraste de iluminación"*).
   - Muestre que el panel derecho actualiza en tiempo real la Tasa de Aceptación (%) y la Diversidad Visual.
   - Presione `Descargar user_decisions.json` para evidenciar la trazabilidad de datos.

4. **Ejecución del Agente Explicador LLM:**
   - En la Sección 3, presione `Generar Explicación con Agente IA`.
   - Muestre el reporte del agente: la lista de variaciones aceptadas y rechazadas, la explicación de cada decisión y la fidelidad calculada contra el registro JSON.

---

## Ubicación de Entregables de Sustentación

Los entregables finales están en la carpeta [`entregable/`](entregable/):

* **Informe técnico:** `Informe_Proyecto2_Grupo7.pdf`. Su fuente es [`material_apoyo/informe/informe.md`](material_apoyo/informe/informe.md).
* **Presentación:** `Presentacion_Proyecto2_Grupo7.pptx`. El guion de la exposición está en [`material_apoyo/presentacion/guion_exposicion.md`](material_apoyo/presentacion/guion_exposicion.md).
* **Guion del video demostrativo:** [`material_apoyo/video/guion_video.md`](material_apoyo/video/guion_video.md).
* **Guía técnica del código:** [`TECHNICAL_GUIDE.md`](TECHNICAL_GUIDE.md).
