import shutil
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from PIL import Image

HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[1]
RESULTS = PROJECT_ROOT / "data" / "processed" / "colab_v1_img2img_sin_preservacion"
CAPTURES = Path(sys.argv[1]) if len(sys.argv) > 1 else None
FIGURES = HERE / "figuras"
FIGURES.mkdir(exist_ok=True)

INK = "#1f2937"
BLUE = "#dbeafe"
GREEN = "#dcfce7"
AMBER = "#fef3c7"
GREY = "#f3f4f6"


def box(ax, x, y, w, h, title, body, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08", fc=color, ec=INK, lw=1))
    ax.text(x + w / 2, y + h - 0.16, title, ha="center", va="top", fontsize=8.6, weight="bold", color=INK)
    ax.text(x + w / 2, y + h - 0.48, body, ha="center", va="top", fontsize=7.1, color=INK, linespacing=1.35)


def arrow(ax, start, end, label=None):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=12, lw=1.1, color=INK))
    if label:
        ax.text((start[0] + end[0]) / 2, (start[1] + end[1]) / 2 + 0.12, label, ha="center", fontsize=7, color="#4b5563")


def architecture() -> None:
    fig, ax = plt.subplots(figsize=(11, 4.6))
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 4.6)
    ax.axis("off")

    box(ax, 0.1, 2.7, 2.0, 1.6, "1. Entrada", "Foto del usuario\nPaquete de 5 estilos\nPrompt libre opcional", GREY)
    box(ax, 2.5, 2.7, 2.0, 1.6, "2. Filtro ético", "safety.py\nNormalización NFKD\nLista léxica + regex\nBloquea antes de la GPU", AMBER)
    box(ax, 4.9, 2.7, 2.0, 1.6, "3. Preproceso", "Detección facial (Haar)\nRecorte cuadrado 512 px\nBordes Canny", GREY)
    box(ax, 7.3, 2.7, 3.6, 1.6, "4. Motor generativo (GPU)",
        "Servidor FastAPI en Colab (Tesla T4)\nIntermedio: SD 1.5 + ControlNet Canny (img2img)\nBásico: SD 1.5 img2img sin ControlNet\nLoRA público detail-tweaker (escala 0,6)\nRespaldo sin GPU: filtro OpenCV", BLUE)

    box(ax, 7.3, 0.3, 3.6, 1.7, "5. Interfaz Streamlit", "5 variaciones en estado Pendiente\nAceptar / Rechazar por imagen\nCalificación 1-5 y comentario", GREEN)
    box(ax, 4.9, 0.3, 2.0, 1.7, "6. Registro", "user_decisions.json\nSesión por participante\nImágenes y tiempos", GREY)
    box(ax, 2.5, 0.3, 2.0, 1.7, "7. Agente explicador", "Gemini 3.5 Flash Lite\n(respaldo: otros modelos)\nAgente de reglas offline", BLUE)
    box(ax, 0.1, 0.3, 2.0, 1.7, "8. Salida y control", "Aceptadas y rechazadas\nExplicación y\nrecomendaciones\nFidelidad vs. JSON", GREEN)

    arrow(ax, (2.1, 3.5), (2.5, 3.5))
    arrow(ax, (4.5, 3.5), (4.9, 3.5))
    arrow(ax, (6.9, 3.5), (7.3, 3.5), "base64")
    arrow(ax, (9.1, 2.7), (9.1, 2.0), "5 imágenes")
    arrow(ax, (7.3, 1.15), (6.9, 1.15))
    arrow(ax, (4.9, 1.15), (4.5, 1.15))
    arrow(ax, (2.5, 1.15), (2.1, 1.15))
    ax.text(3.5, 2.4, "si el prompt infringe las reglas: aviso y no se genera", ha="center", fontsize=7, color="#92400e", style="italic")
    fig.savefig(FIGURES / "fig1_arquitectura.png", dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def entrada() -> None:
    original = Image.open(RESULTS / "00_foto_original.png").convert("RGB")
    crop = Image.open(RESULTS / "01_entrada_512.png").convert("RGB")
    edges = Image.open(RESULTS / "02_canny.png").convert("RGB")
    height = 360
    original = original.resize((int(original.width * height / original.height), height))
    crop = crop.resize((height, height))
    edges = edges.resize((height, height))
    gap = 12
    sheet = Image.new("RGB", (original.width + 2 * height + 2 * gap, height), "white")
    sheet.paste(original, (0, 0))
    sheet.paste(crop, (original.width + gap, 0))
    sheet.paste(edges, (original.width + height + 2 * gap, 0))
    sheet.save(FIGURES / "fig2_entrada_preprocesamiento.png")


def copy_results() -> None:
    shutil.copy(RESULTS / "resumen_nivel_intermedio_controlnet.png", FIGURES / "fig3_intermedio.png")
    shutil.copy(RESULTS / "resumen_nivel_basico_img2img.png", FIGURES / "fig4_basico.png")
    shutil.copy(RESULTS / "resumen_barrido_strength.png", FIGURES / "fig5_barrido.png")


def captures() -> None:
    if not CAPTURES:
        return
    full = Image.open(CAPTURES / "ui_03_agente.png").convert("RGB")
    full.crop((300, 330, 1600, 1300)).save(FIGURES / "fig6_interfaz_votacion.png")
    full.crop((340, 2560, 1560, 3900)).save(FIGURES / "fig7_agente.png")
    safety = Image.open(CAPTURES / "ui_04_filtro_etico.png").convert("RGB")
    safety.crop((0, 1250, 300, 1620)).save(FIGURES / "fig8_filtro.png")
    full.crop((0, 0, 1600, 2500)).save(FIGURES / "anexo_interfaz_completa.png")


if __name__ == "__main__":
    architecture()
    entrada()
    copy_results()
    captures()
    print(sorted(p.name for p in FIGURES.iterdir()))
