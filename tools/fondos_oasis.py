"""Recorta el fondo blanco de las fotos de producto de Oasis Animal y las apoya sobre el fondo de la marca.

Fuente: elpasaje-app/static/productos/oasis-animal (originales 4960 px). Salida: static/web/oasis-animal/*_oasis.jpg
(1200 px). Idempotente. Uso: python tools/fondos_oasis.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

ORIGEN = Path.home() / "elpasaje-app" / "static" / "productos" / "oasis-animal"
DESTINO = Path(__file__).resolve().parent.parent / "static" / "web" / "oasis-animal"
FOTOS = ["clip_dispensador_A", "clip_dispensador_B", "perrito_globo_2", "soporte_comedero", "soporte_comedero_cruz"]
LADO = 1200
FONDO_CLARO, FONDO_OSCURO = (224, 235, 215), (163, 196, 146)  # tintes del verde Oasis #8FB67D
SOMBRA = (88, 120, 74)


def mascara(im: Image.Image) -> Image.Image:
    """Fondo = blanco conectado al borde (flood fill), así no se come los blancos del producto."""
    chico = im.convert("RGB").resize((im.width // 4, im.height // 4))
    marca = chico.copy()
    for xy in [(0, 0), (chico.width - 1, 0), (0, chico.height - 1), (chico.width - 1, chico.height - 1)]:
        ImageDraw.floodfill(marca, xy, (255, 0, 255), thresh=38)
    px = marca.load()
    m = Image.new("L", chico.size, 255)
    mp = m.load()
    for y in range(chico.height):
        for x in range(chico.width):
            if px[x, y] == (255, 0, 255) or min(chico.getpixel((x, y))) > 236:
                mp[x, y] = 0
    m = m.filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(1.2))
    return m.resize(im.size, Image.LANCZOS)


def fondo() -> Image.Image:
    """Degradé radial suave: luz arriba al centro, verde más profundo en los bordes."""
    f = Image.new("RGB", (LADO, LADO), FONDO_OSCURO)
    luz = Image.new("L", (LADO, LADO), 0)
    ImageDraw.Draw(luz).ellipse([-LADO * .25, -LADO * .35, LADO * 1.25, LADO * 1.05], fill=255)
    luz = luz.filter(ImageFilter.GaussianBlur(LADO * .18))
    return Image.composite(Image.new("RGB", (LADO, LADO), FONDO_CLARO), f, luz)


def componer(nombre: str) -> Path:
    im = Image.open(ORIGEN / f"{nombre}.jpg").convert("RGB")
    m = mascara(im)
    caja = m.point(lambda v: 255 if v > 128 else 0).getbbox()
    im, m = im.crop(caja), m.crop(caja)
    escala = (LADO * .70) / max(im.size)
    tam = (int(im.width * escala), int(im.height * escala))
    im, m = im.resize(tam, Image.LANCZOS), m.resize(tam, Image.LANCZOS)
    lienzo = fondo()
    x, y = (LADO - tam[0]) // 2, int(LADO * .47 - tam[1] / 2)
    sombra = Image.new("L", (LADO, LADO), 0)
    base = y + tam[1]
    ImageDraw.Draw(sombra).ellipse([x + tam[0] * .12, base - LADO * .03, x + tam[0] * .88, base + LADO * .012], fill=150)
    sombra = sombra.filter(ImageFilter.GaussianBlur(LADO * .014))
    lienzo = Image.composite(Image.new("RGB", (LADO, LADO), SOMBRA), lienzo, sombra)
    lienzo.paste(im, (x, y), m)
    DESTINO.mkdir(parents=True, exist_ok=True)
    salida = DESTINO / f"{nombre}_oasis.jpg"
    lienzo.save(salida, quality=84, optimize=True, progressive=True)
    return salida


if __name__ == "__main__":
    for n in FOTOS:
        s = componer(n)
        print(s.name, round(s.stat().st_size / 1024), "KB")
