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
> Genera los retratos con Stable Diffusion 1.5 + ControlNet Canny fotorrealistas reales (con trajes oscuros, corbatas, sacos y fondos de oficina corporativa desenfocados) en 3 segundos por foto, ejecutándose en los 15 GB de VRAM de la GPU T4 de Google Colab sin consumir memoria de la computadora personal.

### Paso 1: Abrir el Notebook en Colab
1. Ingrese a Google Colab.
2. Haga clic en Subir (Upload) y seleccione el archivo del repositorio:  
   `Project-II/notebooks/controlnet_portrait_pipeline.ipynb`

### Paso 2: Activar la GPU Gratuita
En la barra de menú superior de Google Colab:
- Vaya a: Entorno de ejecución (Runtime) > Cambiar tipo de entorno (Change runtime type).
- En Acelerador de hardware, seleccione T4 GPU (Gratuito).
- Haga clic en Guardar.

### Paso 3: Ejecutar la Celda de Servidor y Túnel Cloudflare
- Ejecute las celdas 1, 2 y 3 del notebook (o presione `Ctrl + F9` para ejecutar todo).
- La Celda 3 descargará los modelos de Hugging Face (`lllyasviel/control_v11p_sd15_canny` + `runwayml/stable-diffusion-v1-5`), levantará el servidor FastAPI (`src/gpu_server.py`) en segundo plano y creará un túnel público gratuito con Cloudflare.
- En la salida de la celda observará la URL pública:
  ```text
  Your quick Tunnel has been created! Visit it at:
  https://palabras-aleatorias.trycloudflare.com
  ```
- Copie esa URL (la que termina en `.trycloudflare.com`).

### Paso 4: Conectar la Aplicación Local de Streamlit
1. En su computadora, inicie la interfaz web:
   - Haga doble clic en `run_app.bat` (en Windows) o ejecute `streamlit run ui/app.py`.
2. En la barra lateral izquierda de Streamlit, en "Nivel Técnico del Motor Generativo", seleccione:
   - `Servidor GPU Remoto (Google Colab / MV)`.
3. En el campo que aparece ("URL del Servidor GPU"), pegue la URL de Cloudflare que copió.
4. Presione el botón `Probar Conexión GPU`.
5. Verá el indicador: `Conectado: NVIDIA Tesla T4 (CUDA Activo)`.

### Paso 5: Generar y Evaluar en Tiempo Real
- Suba su fotografía de entrada (o use la muestra sintética).
- Seleccione el paquete deseado (ej. Paquete Corporativo Multiplataforma).
- Haga clic en `Generar Variaciones Visuales`.
- La GPU de Colab procesará la imagen en 3 segundos por foto y las mostrará de inmediato en la interfaz web con los trajes y fondos correspondientes.

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
2. Seleccione el modo `Nivel Intermedio (ControlNet + img2img)` o `Nivel Básico`.
3. El motor local ejecuta automáticamente:
   - Detección y centrado facial con OpenCV Haar Cascade.
   - Extracción de restricciones anatómicas faciales con ControlNet Canny.
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
   - Exponga el reporte emitido por el agente: resume la tasa de adopción, justifica por qué se eligieron los esquemas formales y por qué se descartaron los informales, con una Fidelidad Factual del 100%.

---

## Ubicación de Entregables de Sustentación

Todos los archivos requeridos para la evaluación final se encuentran en el repositorio:

* Diapositivas Interactivas: [`docs/final_submission/presentation.html`](docs/final_submission/presentation.html)  
  *(Proyectables en pantalla completa con F11; navegación con las flechas del teclado).*
* Guión de Exposición Oral: [`docs/final_submission/presentation_script.md`](docs/final_submission/presentation_script.md)  
  *(Guión detallado para José, Matías y Alejandro diapositiva por diapositiva).*
* Informe Técnico Escrito: [`docs/final_submission/technical_report.md`](docs/final_submission/technical_report.md)  
  *(Documento formal que cubre los 6 criterios de la rúbrica oficial de 20 puntos).*
* Guía Técnica de Arquitectura: [`TECHNICAL_GUIDE.md`](TECHNICAL_GUIDE.md)
