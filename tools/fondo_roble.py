"""Apoya un recorte PNG (Adobe) sobre un fondo de madera oscura sintética con sombra. Uso: fondo_roble.py recorte.png salida.jpg [ancho alto]"""
import sys
import numpy as np
from PIL import Image, ImageFilter

src, dst = sys.argv[1], sys.argv[2]
W, H = (int(sys.argv[3]), int(sys.argv[4])) if len(sys.argv) > 4 else (1600, 2000)
rng = np.random.default_rng(7)

# vetas de roble: ondas a lo largo de X con ruido suave
y = np.arange(H)[:, None]; x = np.arange(W)[None, :]
ruido = Image.fromarray((rng.random((H // 30, 6)) * 255).astype("uint8")).resize((W, H), Image.BICUBIC)
r = np.asarray(ruido, float) / 255
vetas = np.sin(y / 3.2 + r * 4 + np.sin(x / 700.0) * 1.5) * 0.5 + 0.5
fino = np.asarray(Image.fromarray((rng.random((H, W // 150)) * 255).astype("uint8")).resize((W, H), Image.BICUBIC), float) / 255
t = 0.30 * vetas + 0.35 * r + 0.35 * fino
oscuro = np.array([52, 32, 18]); claro = np.array([120, 80, 46])
img = oscuro + (claro - oscuro) * t[..., None]
# luz cenital y viñeta
cx, cy = W / 2, H * 0.42
d = np.sqrt(((x - cx) / W) ** 2 + ((y - cy) / H) ** 2)
img *= np.clip(1.15 - d * 1.6, 0.25, 1.15)[..., None]
fondo = Image.fromarray(np.clip(img, 0, 255).astype("uint8"))

obj = Image.open(src).convert("RGBA")
obj = obj.crop(obj.getchannel("A").getbbox())
esc = min(W * 0.86 / obj.width, H * 0.62 / obj.height)
obj = obj.resize((int(obj.width * esc), int(obj.height * esc)), Image.LANCZOS)
ox, oy = (W - obj.width) // 2, int(H * 0.50 - obj.height / 2)

sombra = Image.new("L", (W, H), 0)
a = obj.getchannel("A").point(lambda v: 170 if v > 20 else 0)
sombra.paste(a, (ox + 18, oy + 40))
sombra = sombra.filter(ImageFilter.GaussianBlur(45))
fondo.paste((10, 6, 3), (0, 0), sombra)
fondo.paste(obj, (ox, oy), obj)
fondo.save(dst, quality=92)
print(dst, fondo.size)
