"""Apoya recortes PNG (Adobe) sobre un fondo de madera oscura sintética, con sombra.

Uso simple:   fondo_roble.py recorte.png salida.jpg [ancho alto]
Uso por capas (desde Python):
    from fondo_roble import fondo, apoyar
    f = fondo(2000, 1250); apoyar(f, "caja.png", ancho=0.6, cx=0.45, cy=0.45); f.convert("RGB").save(...)
"""
import sys
import numpy as np
from PIL import Image, ImageFilter


def fondo(W, H, semilla=7):
    rng = np.random.default_rng(semilla)
    y = np.arange(H)[:, None]; x = np.arange(W)[None, :]
    ruido = Image.fromarray((rng.random((H // 30, 6)) * 255).astype("uint8")).resize((W, H), Image.BICUBIC)
    r = np.asarray(ruido, float) / 255
    vetas = np.sin(y / 3.2 + r * 4 + np.sin(x / 700.0) * 1.5) * 0.5 + 0.5
    fino = np.asarray(Image.fromarray((rng.random((H, max(W // 150, 2))) * 255).astype("uint8")).resize((W, H), Image.BICUBIC), float) / 255
    t = 0.30 * vetas + 0.35 * r + 0.35 * fino
    oscuro = np.array([52, 32, 18]); claro = np.array([120, 80, 46])
    img = oscuro + (claro - oscuro) * t[..., None]
    cx, cy = W / 2, H * 0.42
    d = np.sqrt(((x - cx) / W) ** 2 + ((y - cy) / H) ** 2)
    img *= np.clip(1.15 - d * 1.6, 0.25, 1.15)[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype("uint8")).convert("RGBA")


def apoyar(base, src, ancho=None, alto=None, cx=0.5, cy=0.5, giro=0, sombra=(18, 40, 45)):
    """Pega el recorte centrado en (cx, cy) (fracciones), con ancho o alto relativo al lienzo. Devuelve la caja (x, y, w, h)."""
    W, H = base.size
    obj = Image.open(src).convert("RGBA") if isinstance(src, str) else src
    obj = obj.crop(obj.getchannel("A").getbbox())
    if giro:
        obj = obj.rotate(giro, resample=Image.BICUBIC, expand=True)
    esc = (W * ancho / obj.width) if ancho else (H * alto / obj.height)
    obj = obj.resize((int(obj.width * esc), int(obj.height * esc)), Image.LANCZOS)
    ox, oy = int(W * cx - obj.width / 2), int(H * cy - obj.height / 2)
    dx, dy, blur = sombra
    s = Image.new("L", (W, H), 0)
    s.paste(obj.getchannel("A").point(lambda v: 170 if v > 20 else 0), (ox + dx, oy + dy))
    s = s.filter(ImageFilter.GaussianBlur(blur))
    base.paste((10, 6, 3, 255), (0, 0), s)
    base.alpha_composite(obj, (max(ox, 0), max(oy, 0)) if ox >= 0 and oy >= 0 else (0, 0))
    return ox, oy, obj.width, obj.height


if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    W, H = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (1600, 2000)
    f = fondo(W, H)
    o = Image.open(src).convert("RGBA"); o = o.crop(o.getchannel("A").getbbox())
    if W * 0.86 / o.width <= H * 0.62 / o.height:
        apoyar(f, o, ancho=0.86, cy=0.50)
    else:
        apoyar(f, o, alto=0.62, cy=0.50)
    f.convert("RGB").save(dst, quality=92)
    print(dst, f.size)
