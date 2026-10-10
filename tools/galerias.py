"""tools/galerias.py — Fotos web livianas + galería por línea (catálogo público, 10/10/2026).

1. Toma las fotos originales (static/productos/<linea>/, hasta 4960 px y 1,8 MB) y genera versiones web en
   static/web/<linea>/ (lado mayor 1200 px, JPEG calidad 82, orientación corregida). Las originales no se tocan.
2. Inserta (o actualiza) en cada página una sección "Galería" antes del <footer>: grilla que se adapta al celular,
   lazy loading, texto alternativo y toque para ampliar. Se puede correr las veces que haga falta (idempotente).

Qué NO se publica (decisión 10/10): fotos con una persona real (litofanía), con el nombre de la mascota de un
cliente (chapas "Poncho"), productos sin alta en el catálogo (clip dispensador) y marcas de terceros
(Hello Kitty, Ferrari, Pokémon: IP_RESTRINGIDA).

Uso: python tools/galerias.py
"""
from __future__ import annotations

import html
import re
from pathlib import Path

from PIL import Image, ImageOps

C = Path(__file__).resolve().parents[1]
WEB = C / "static" / "web"
EXTRA = Path.home() / "elpasaje-app" / "assets" / "sport"  # cajitas en mejor calidad que las miniaturas

# página → (carpeta de fotos, color de acento, [(archivo, texto alternativo)])
GALERIAS = {
    "magnitud19.html": ("magnitud19", "#C9A84C", [
        ("calavera_negro_A.jpg", "Calavera paramétrica negra, vista lateral"),
        ("calavera_violeta_frente.jpg", "Calavera paramétrica violeta, de frente"),
        ("calaveras_violeta_negro_A.jpg", "Calaveras violeta y negra juntas"),
        ("calaveras_comparacion_A.jpg", "Comparación de tamaños de las calaveras"),
        ("calavera_violeta_atras.jpg", "Calavera violeta, vista posterior"),
        ("calaveras_C.jpg", "Calaveras paramétricas en capas")]),
    "core-tech.html": ("core-tech", "#0E7E78", [
        ("organizador_escritorio.jpg", "Organizador de escritorio impreso en 3D"),
        ("soporte_apple_watch_1.jpg", "Soporte para Apple Watch"),
        ("soporte_apple_watch_2.jpg", "Soporte para Apple Watch, otra vista"),
        ("soporte_relojes.jpg", "Soporte para relojes")]),
    "luminis.html": ("luminis", "#B8860B", [
        ("lampara_luna_1.jpg", "Lámpara luna impresa en 3D"),
        ("lampara_luna_2.jpg", "Lámpara luna encendida")]),
    "oasis-animal.html": ("oasis-animal", "#F472B6", [
        ("perrito_globo_1.jpg", "Llavero Perrito Globo"),
        ("perrito_globo_2.jpg", "Llavero Perrito Globo, detalle"),
        ("soporte_comedero.jpg", "Soporte de comedero Patita"),
        ("soporte_comedero_cruz.jpg", "Pata del soporte de comedero, grabada")]),
    "sport.html": ("sport", "#F97316", [
        ("@cajita_afa.jpg", "Cajita porta-figuritas AFA"),
        ("@cajita_argentina.jpg", "Cajita porta-figuritas Argentina"),
        ("@cajita_fifa26.jpg", "Cajita porta-figuritas FIFA 26"),
        ("@cajita_variantes.jpg", "Variantes de color de las cajitas")]),
}
INICIO, FIN = "<!-- GALERIA:INICIO (tools/galerias.py) -->", "<!-- GALERIA:FIN -->"


def web(carpeta: str, archivo: str) -> str:
    origen = EXTRA / archivo[1:] if archivo.startswith("@") else C / "static" / "productos" / carpeta / archivo
    nombre = archivo.lstrip("@")
    destino = WEB / carpeta / nombre
    destino.parent.mkdir(parents=True, exist_ok=True)
    im = ImageOps.exif_transpose(Image.open(origen)).convert("RGB")
    im.thumbnail((1200, 1200), Image.LANCZOS)
    im.save(destino, "JPEG", quality=82, optimize=True, progressive=True)
    return f"static/web/{carpeta}/{nombre}"


def seccion(acento: str, fotos: list[tuple[str, str]]) -> str:
    items = "\n".join(
        f'    <a class="epg-item" href="{src}" target="_blank" rel="noopener"><img src="{src}" alt="{html.escape(alt)}" '
        f'loading="lazy" decoding="async"><span>{html.escape(alt)}</span></a>' for src, alt in fotos)
    return f"""{INICIO}
<section class="epg" aria-label="Galería de productos">
  <style>
    .epg{{max-width:1200px;margin:0 auto;padding:48px 16px}}
    .epg h2{{margin:0 0 6px;font-size:clamp(1.4rem,4vw,2rem)}}
    .epg p.epg-sub{{margin:0 0 20px;opacity:.75}}
    .epg-grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:12px}}
    .epg-item{{display:block;border-radius:14px;overflow:hidden;background:#fff;border:1px solid rgba(0,0,0,.08);
              text-decoration:none;color:inherit;box-shadow:0 2px 10px rgba(0,0,0,.06);transition:transform .15s}}
    .epg-item:hover{{transform:translateY(-2px);border-color:{acento}}}
    .epg-item img{{display:block;width:100%;aspect-ratio:1/1;object-fit:cover;background:#f4f4f4}}
    .epg-item span{{display:block;padding:8px 10px;font-size:.82rem;line-height:1.3}}
    @media (min-width:700px){{.epg-grid{{grid-template-columns:repeat(auto-fill,minmax(220px,1fr))}}}}
  </style>
  <h2>Galería</h2>
  <p class="epg-sub">Piezas reales, impresas en nuestro taller de Buenos Aires.</p>
  <div class="epg-grid">
{items}
  </div>
</section>
{FIN}
"""


def main() -> None:
    for pagina, (carpeta, acento, fotos) in GALERIAS.items():
        ruta = C / pagina
        texto = ruta.read_text(encoding="utf-8")
        bloque = seccion(acento, [(web(carpeta, a), alt) for a, alt in fotos])
        if INICIO in texto:
            texto = re.sub(re.escape(INICIO) + r".*?" + re.escape(FIN) + r"\n?", bloque, texto, flags=re.S)
        else:
            m = re.search(r"<footer", texto, flags=re.I)
            corte = m.start() if m else texto.lower().rindex("</body>")
            texto = texto[:corte] + bloque + texto[corte:]
        ruta.write_text(texto, encoding="utf-8")
        print(f"{pagina}: {len(fotos)} fotos")


if __name__ == "__main__":
    main()
