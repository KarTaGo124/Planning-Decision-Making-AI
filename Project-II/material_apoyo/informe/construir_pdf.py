import subprocess
import sys
from pathlib import Path

import markdown
from pypdf import PdfReader

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "informe.md"
HTML = HERE / "informe.html"
PDF = HERE.parents[1] / "entregable" / "Informe_Proyecto2_Grupo7.pdf"
BROWSERS = [
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
]

CSS = """
@page { size: A4; margin: 17mm 17mm 16mm 17mm;
  @bottom-center { content: counter(page); font: 9pt 'Segoe UI', Arial, sans-serif; color: #6b7280; } }
html { font-family: 'Segoe UI', Calibri, Arial, sans-serif; font-size: 10.2pt; line-height: 1.42; color: #111827; }
body { margin: 0; }
p { margin: 0 0 6pt 0; text-align: justify; hyphens: auto; }
h1 { font-size: 16.5pt; line-height: 1.22; margin: 4pt 0 6pt; color: #0f172a; }
h2 { font-size: 12.4pt; margin: 12pt 0 5pt; color: #0f172a; border-bottom: 1px solid #cbd5e1; padding-bottom: 2pt; break-after: avoid; }
ul, ol { margin: 0 0 6pt 0; padding-left: 17pt; }
li { margin: 0 0 2.5pt 0; text-align: justify; }
code { font-family: Consolas, 'Courier New', monospace; font-size: 8.9pt; background: #f1f5f9; padding: 0 2pt; border-radius: 2pt; }
pre { font-family: Consolas, 'Courier New', monospace; font-size: 8pt; line-height: 1.3; background: #f8fafc; border: 1px solid #e2e8f0; padding: 6pt 8pt; white-space: pre-wrap; margin: 4pt 0 8pt; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0 9pt; font-size: 8.9pt; break-inside: avoid; }
th { background: #e2e8f0; text-align: left; padding: 3pt 5pt; border: 1px solid #cbd5e1; }
td { padding: 3pt 5pt; border: 1px solid #e2e8f0; vertical-align: top; }
figure { margin: 6pt 0 9pt; text-align: center; break-inside: avoid; }
figure img { display: block; margin: 0 auto; }
figcaption { font-size: 8.6pt; color: #374151; margin-top: 3pt; text-align: center; }
.portada { border-bottom: 2px solid #0f172a; padding-bottom: 6pt; margin-bottom: 9pt; }
.portada .inst { font-size: 8.8pt; color: #475569; margin: 0; text-align: left; }
.portada .sub { font-size: 10pt; color: #1f2937; margin: 0 0 4pt; text-align: left; }
.portada .meta { font-size: 9pt; color: #1f2937; margin: 0; text-align: left; line-height: 1.5; }
.formula { text-align: center; font-family: 'Cambria Math', Cambria, serif; font-size: 10.5pt; margin: 4pt 0 8pt; }
.bibliografia { break-before: page; }
.bibliografia p { text-align: left; padding-left: 16pt; text-indent: -16pt; font-size: 9.2pt; margin-bottom: 4pt; }
.anexos { break-before: page; }
.anexos h2 { margin-top: 8pt; }
.dos { display: flex; gap: 10pt; align-items: flex-start; }
.dos figure:first-child { flex: 3; }
.dos figure:last-child { flex: 1; }
.dos figure:first-child img { max-height: 150mm; width: auto !important; max-width: 100%; }
pre { break-inside: avoid; }
"""


def main() -> None:
    body = markdown.markdown(SOURCE.read_text(encoding="utf-8"), extensions=["tables", "md_in_html"])
    HTML.write_text(
        f"<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'><title>Informe Proyecto 2 - Grupo 7</title>"
        f"<style>{CSS}</style></head><body>{body}</body></html>",
        encoding="utf-8",
    )
    browser = next((b for b in BROWSERS if b.exists()), None)
    if browser is None:
        sys.exit("No se encontró Edge ni Chrome para generar el PDF.")
    subprocess.run(
        [str(browser), "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={PDF}", HTML.as_uri()],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )

    reader = PdfReader(str(PDF))
    pages = [page.extract_text() or "" for page in reader.pages]
    bibliography = next(i for i, text in enumerate(pages) if "Bibliografía" in text and "Amershi" in text)
    annexes = next(i for i, text in enumerate(pages) if "Anexo A. Ejemplos" in text)
    print(f"PDF: {PDF}")
    print(f"total {len(pages)} páginas | cuerpo {bibliography} | bibliografía {annexes - bibliography} | anexos {len(pages) - annexes}")


if __name__ == "__main__":
    main()
