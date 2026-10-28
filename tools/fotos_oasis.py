"""Fotos de la carpeta de Drive Oasis_Animal -> fotos web con el mismo tratamiento (encuadre cuadrado, color parejo).

Uso: python tools/fotos_oasis.py <carpeta con las fotos bajadas de Drive>
Salida: static/web/oasis-animal/<nombre>.jpg (1000 px). Idempotente. Las fotos con fondo real no se recortan:
se encuadran y se igualan en luz y calidez para que se vean de la misma sesión.
"""
import sys
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps

DESTINO = Path(__file__).resolve().parent.parent / "static" / "web" / "oasis-animal"
LADO = 1000
# nombre web: (archivo de Drive, centro x, centro y, zoom)  — centro en fracción de la foto; zoom >1 acerca
FOTOS = {
    "estacion_beige":      ("20260708_182116.jpg", .50, .55, 1.0),
    "estacion_verde":      ("20260712_201304.jpg", .50, .52, 1.0),
    "estacion_colores":    ("IMG-20260820-WA0047.jpg", .50, .50, 1.0),
    "estacion_azul":       ("IMG-20260820-WA0046.jpg", .50, .50, 1.0),
    "comedero_hueso":      ("IMG-20260701-WA0013.jpg", .50, .46, 1.06),
    "comedero_salvia":     ("IMG-20260708-WA0040.jpg", .50, .55, 1.1),
    "comedero_gris":       ("IMG-20260717-WA0035.jpg", .50, .50, 1.0),
    "dispensador_trio":    ("IMG-20260717-WA0036.jpg", .50, .50, 1.0),
    "dispensador_colores": ("IMG-20260701-WA0011.jpg", .50, .52, 1.06),
    "dispensador_llavero": ("IMG-20260726-WA0001.jpg", .40, .45, 1.2),
    "perritos_fila":       ("IMG-20250727-WA0033.jpg", .50, .50, 1.0),
    "perritos_colores":    ("IMG-20250727-WA0032.jpg", .50, .50, 1.0),
    "pelota_huella":       ("IMG-20260312-WA0040.jpg", .50, .50, 1.0),
}


def tratar(origen: Path, cx: float, cy: float, zoom: float) -> Image.Image:
    im = ImageOps.exif_transpose(Image.open(origen)).convert("RGB")
    lado = int(min(im.size) / zoom)
    x = min(max(int(im.width * cx - lado / 2), 0), im.width - lado)
    y = min(max(int(im.height * cy - lado / 2), 0), im.height - lado)
    im = im.crop((x, y, x + lado, y + lado)).resize((LADO, LADO), Image.LANCZOS)
    im = ImageOps.autocontrast(im, cutoff=1)
    im = ImageEnhance.Brightness(im).enhance(1.04)
    r, g, b = im.split()  # un toque cálido, como las fotos de @oasisanimal
    r = r.point(lambda v: min(255, int(v * 1.03)))
    b = b.point(lambda v: int(v * .97))
    return ImageEnhance.Color(Image.merge("RGB", (r, g, b))).enhance(1.05)


if __name__ == "__main__":
    carpeta = Path(sys.argv[1])
    DESTINO.mkdir(parents=True, exist_ok=True)
    for nombre, (archivo, cx, cy, z) in FOTOS.items():
        f = carpeta / archivo
        if not f.exists():
            print("FALTA", archivo); continue
        s = DESTINO / f"{nombre}.jpg"
        tratar(f, cx, cy, z).save(s, quality=82, optimize=True, progressive=True)
        print(s.name, round(s.stat().st_size / 1024), "KB")
