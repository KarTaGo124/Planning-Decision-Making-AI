from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
FIGURES = HERE.parents[1] / "informe" / "figuras"
OUT = HERE / "img"
OUT.mkdir(exist_ok=True)

TILE = 384
LABEL_BAND = 28


def tiles(name: str, prefix: str, count: int) -> None:
    strip = Image.open(FIGURES / name).convert("RGB")
    for index in range(count):
        box = (index * TILE, LABEL_BAND, (index + 1) * TILE, LABEL_BAND + TILE)
        strip.crop(box).save(OUT / f"{prefix}_{index}.png")


def preprocessing() -> None:
    sheet = Image.open(FIGURES / "fig2_entrada_preprocesamiento.png").convert("RGB")
    width, height = sheet.size
    original_width = width - 2 * height - 24
    sheet.crop((0, 0, original_width, height)).save(OUT / "pre_original.png")
    sheet.crop((original_width + 12, 0, original_width + 12 + height, height)).save(OUT / "pre_recorte.png")
    sheet.crop((width - height, 0, width, height)).save(OUT / "pre_canny.png")


if __name__ == "__main__":
    tiles("fig3_intermedio.png", "intermedio", 6)
    tiles("fig4_basico.png", "basico", 6)
    tiles("fig5_barrido.png", "barrido", 4)
    preprocessing()
    print(sorted(p.name for p in OUT.iterdir()))
