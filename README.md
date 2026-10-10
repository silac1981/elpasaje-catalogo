# El Pasaje 3D Studio — catálogo público

Páginas de las líneas y catálogos (`exports/*.json`) servidos por GitHub Pages:
https://silac1981.github.io/elpasaje-catalogo/

**Repo público a propósito y sin historial heredado.** Solo contenido pensado para clientes:
nada de código de la app, bases, credenciales ni datos de otros proyectos.
La app interna vive en `silac1981/elpasaje-app` (privado). Los JSON se regeneran desde la app
(tab Control → "Regenerar catálogos") y se copian acá.

Antes de cada push: `git grep -n -i -E "contraseña|password|@elpasaje\.com|costo material|cost_kg"` tiene que dar vacío
(salvo textos de marketing revisados).
