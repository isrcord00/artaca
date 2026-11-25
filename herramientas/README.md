# Gestor de contenidos — Artesanía Tauro C.A.

Pequeña herramienta de escritorio (Python) para que el dueño del negocio
agregue **productos** y **noticias** al sitio sin tocar código ni usar GitHub.

Todo se hace desde una consola con preguntas guiadas paso a paso:

- Optimiza y recorta **automáticamente** las fotos que le des (jpg/png).
- Valida los datos antes de escribir (categorías, textos, duplicados).
- Puede **generar una portada** para las noticias que no tengan foto.
- Publica con un solo comando (o previsualiza antes con `--simular`).

---

## Requisitos

1. **Python 3.9 o superior** — https://www.python.org/downloads/
   En Windows, marca la casilla *"Add Python to PATH"* durante la instalación.
2. **Pillow** (manejo de imágenes). Se instala con:

   ```
   pip install -r requirements.txt
   ```

   (o solo: `pip install Pillow`)

3. **Git** instalado y con acceso al repositorio del sitio
   (solo es necesario para el comando `publicar`).

---

## Uso rápido

Abre una consola **dentro de la carpeta del proyecto** y lanza:

```
python herramientas/gestor.py
```

Si ejecutas la herramienta **sin comando**, se muestra una ayuda con todos
los comandos disponibles.

---

## Comandos

### 1. Agregar un producto

```
python herramientas/gestor.py alta-producto
```

Te preguntará, uno a uno:

| Dato              | Obligatorio | Detalle                                                     |
| ----------------- | ----------- | ----------------------------------------------------------- |
| Foto              | ✅ Sí       | Ruta de la imagen en tu PC (jpg/png). Se recorta a cuadrado 800×800 y se comprime automáticamente. |
| Nombre            | ✅ Sí       | Ej: `Alpargata Clásica Negra`                               |
| Categoría         | ✅ Sí       | Se elige de la lista: Alpargatas / Cocuizas / Bolsos / Accesorios |
| Descripción corta | ✅ Sí       | 1 línea para el catálogo (máx. 160 caracteres)               |
| Descripción larga | ✅ Sí       | Párrafo para la página del producto. Termina escribiendo `FIN` en una línea propia |
| Destacado         | —           | Si aparece en la página de inicio (solo se recomiendan 3)    |

Al terminar:

- La foto queda optimizada en `public/images/productos/<id>.jpg`
- El producto se agrega a `src/data/productos.json`
- Con `--simular` no escribe nada, solo te muestra lo que haría.

### 2. Agregar una noticia

```
python herramientas/gestor.py alta-noticia
```

Te preguntará:

| Dato       | Obligatorio | Detalle                                                      |
| ---------- | ----------- | ------------------------------------------------------------ |
| Foto       | ❌ Opcional | Si no tienes foto, se genera una **portada decorativa** con los colores del sitio |
| Título     | ✅ Sí       | Ej: `Nueva colección de cocuizas ya disponible`              |
| Resumen    | ✅ Sí       | 1–2 líneas que se ven en el listado de noticias              |
| Contenido  | ✅ Sí       | Artículo completo. Termina escribiendo `FIN` en una línea propia |
| Etiquetas  | —           | Separadas por coma. Ej: `novedades, cocuizas`                 |

Al terminar:

- La portada queda en `public/images/blog/<id>.jpg` (1280×720)
- La noticia se crea en `src/content/noticias/<id>.md`
- La página `noticias` y la propia noticia se generan automáticamente.

### 3. Listar el contenido actual

```
python herramientas/gestor.py listar
```

Muestra todos los productos y noticias publicados en el sitio, con su
identificador (id) para que puedas localizarlos fácilmente.

### 4. Revisar que todo esté en orden

```
python herramientas/gestor.py validar
```

Comprueba:

- Que `productos.json` sea válido y no tenga ids repetidos.
- Que las categorías sean las permitidas.
- Que cada producto/noticia tenga su foto o portada.
- Que cada noticia tenga título, resumen y contenido.

Si encuentra problemas, los lista y sale con error.

> Consejo: ejecuta `validar` después de editar archivos a mano
> y **antes** de publicar.

### 5. Publicar los cambios

```
python herramientas/gestor.py publicar
```

Guarda todo con Git y lo sube a GitHub. El hosting (Cloudflare)
detecta los cambios y **actualiza el sitio en vivo en 1–2 minutos**.

Con `--simular` solo muestra los comandos que ejecutaría, sin tocar nada.

---

## Ejemplo completo (agregar y publicar un producto)

```
python herramientas/gestor.py alta-producto

  📸 Ruta de la foto: C:\Users\Tienda\Fotos\negro.jpg
  🏷️  Nombre: Alpargata Clásica Negra
  📁 Categoría: 1 (Alpargatas)
  📝 Descripción corta: Alpargata artesanal en lona negra, suela de caucho.
  📄 Descripción larga: Hecha a mano por nuestros artesanos...
     FIN
  ⭐ ¿Destacado? (s/n): n

✅ Producto agregado: alpargata-clasica-negra

python herramientas/gestor.py publicar

✅ Cambios enviados. El sitio se actualizará en unos minutos.
```

---

## Preguntas frecuentes

**¿Puedo editar o eliminar productos existentes?**
Esta versión se enfoca en *agregar* contenido nuevo. Para editar o eliminar,
hazlo pidiendo el cambio al desarrollador (o editando `productos.json` a mano
y ejecutando `validar` + `publicar`).

**¿Qué formatos de foto acepta?**
JPG y PNG. La herramienta se encarga de recortar, redimensionar y comprimir
para que el sitio siga siendo rápido.

**Me equivoqué en un texto, ¿puedo corregirlo?**
Sí: edita el archivo correspondiente con cualquier editor de texto y luego
ejecuta `validar` y `publicar`.

**El comando `publicar` da error de permisos.**
Significa que Git no tiene acceso al repositorio en esa máquina. Pídele al
desarrollador que configure las credenciales o publique por ti.
