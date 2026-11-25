#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# =============================================================
# Gestor de contenidos — Artesanía Tauro, C.A.
# -------------------------------------------------------------
# Mini-CMS de línea de comandos para administrar el catálogo y
# las noticias del sitio sin tocar el código ni el diseño.
#
# Comandos:
#   alta-producto  Agrega un producto al catálogo (con foto optimizada)
#   alta-noticia   Agrega una entrada al blog (con portada opcional)
#   listar         Muestra productos y noticias actuales
#   validar        Revisa consistencia de datos e imágenes
#   publicar       Guarda (git commit) y sube (git push) los cambios
#
# Opción global:
#   --simular      Muestra qué haría el comando sin escribir archivos
#
# Requisitos: Python 3.9+ y Pillow  ->  pip install -r herramientas/requirements.txt
# Los cambios publicados llegan en línea en ~2 minutos (Cloudflare).
# =============================================================
from __future__ import annotations

import argparse
import io
import json
import re
import subprocess
import sys
import unicodedata
from datetime import date
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except ImportError:  # Pillow es obligatorio solo para los comandos con imágenes
    Image = None

# -------------------------------------------------------------
# Rutas base (relativas a la ubicación de este script)
# -------------------------------------------------------------
RAIZ = Path(__file__).resolve().parent.parent
RUTA_PRODUCTOS = RAIZ / "src" / "data" / "productos.json"
DIR_NOTICIAS = RAIZ / "src" / "content" / "noticias"
DIR_FOTOS = RAIZ / "public" / "images" / "productos"
DIR_PORTADAS = RAIZ / "public" / "images" / "blog"

CATEGORIAS = ["Alpargatas", "Cocuizas", "Bolsos", "Accesorios"]
FOTO_ANCHO, FOTO_ALTO, FOTO_MAX_KB = 800, 800, 220
PORTADA_ANCHO, PORTADA_ALTO, PORTADA_MAX_KB = 1280, 720, 300

# -------------------------------------------------------------
# Consola: colores y utilidades de salida
# -------------------------------------------------------------
RESET, NEGRITA = "\033[0m", "\033[1m"
CIAN, MAGENTA, VERDE, ROJO, AMARILLO, GRIS = (
    "\033[96m", "\033[95m", "\033[92m", "\033[91m", "\033[93m", "\033[90m",
)

if sys.platform == "win32":
    import os as _os
    _os.system("")  # habilita los colores ANSI en la consola de Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, OSError):
    pass


def titulo(texto: str) -> None:
    print(f"\n{CIAN}{NEGRITA}── {texto} " + "─" * max(0, 60 - len(texto)) + RESET)


def ok(texto: str) -> None:
    print(f"  {VERDE}✔{RESET} {texto}")


def aviso(texto: str) -> None:
    print(f"  {AMARILLO}⚠{RESET} {texto}")


def error(texto: str, salir: bool = True) -> None:
    print(f"  {ROJO}✘ {texto}{RESET}")
    if salir:
        sys.exit(1)


# -------------------------------------------------------------
# Utilidades de texto
# -------------------------------------------------------------
def slugify(texto: str) -> str:
    """Convierte un nombre en un identificador de URL (sin acentos ni espacios)."""
    limpio = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    limpio = re.sub(r"[^a-zA-Z0-9]+", "-", limpio).strip("-").lower()
    return limpio or "sin-nombre"


def escapar_yaml(valor: str) -> str:
    """Prepara un texto para ir entre comillas en el frontmatter."""
    return valor.replace("\\", "\\\\").replace('"', '\\"')


# -------------------------------------------------------------
# Entrada interactiva
# -------------------------------------------------------------
def preguntar(etiqueta: str, defecto: str | None = None) -> str:
    sufijo = f" {GRIS}[{defecto}]{RESET}" if defecto else ""
    while True:
        try:
            respuesta = input(f"  {etiqueta}{sufijo}: ").strip()
        except EOFError:
            if defecto is not None:
                return defecto
            raise
        if respuesta:
            return respuesta
        if defecto is not None:
            return defecto
        aviso("Este dato es obligatorio.")


def preguntar_ruta(etiqueta: str, debe_existir: bool = True) -> Path:
    while True:
        ruta = Path(preguntar(etiqueta)).expanduser()
        if not debe_existir or ruta.is_file():
            return ruta
        error(f"No existe el archivo: {ruta}", salir=False)


def preguntar_sino(etiqueta: str, defecto: bool = False) -> bool:
    sugerencia = "s/n" if defecto is None else ("S/n" if defecto else "s/N")
    try:
        respuesta = input(f"  {etiqueta} {GRIS}[{sugerencia}]{RESET}: ").strip().lower()
    except EOFError:
        return defecto
    if not respuesta:
        return defecto
    return respuesta in ("s", "si", "sí", "y", "yes")


def preguntar_opcion(etiqueta: str, opciones: list[str]) -> str:
    print(f"  {etiqueta}:")
    for numero, opcion in enumerate(opciones, 1):
        print(f"    {numero}) {opcion}")
    while True:
        try:
            elegido = input("  Opción (número): ").strip()
        except EOFError:
            error("Entrada terminada; operación cancelada.")
        if elegido.isdigit() and 1 <= int(elegido) <= len(opciones):
            return opciones[int(elegido) - 1]
        aviso(f"Escribe un número entre 1 y {len(opciones)}.")


def leer_cuerpo(ruta: Path | None) -> str:
    """Lee el cuerpo de una noticia desde un archivo o desde la terminal."""
    if ruta:
        return ruta.expanduser().read_text(encoding="utf-8").strip()
    print("  Escribe o pega el artículo. Para terminar, escribe en una línea propia: FIN")
    lineas: list[str] = []
    while True:
        try:
            linea = input()
        except EOFError:
            break
        if linea.strip() == "FIN":
            break
        lineas.append(linea)
    return "\n".join(lineas).strip()


# -------------------------------------------------------------
# Datos: productos
# -------------------------------------------------------------
def cargar_productos() -> list[dict]:
    try:
        return json.loads(RUTA_PRODUCTOS.read_text(encoding="utf-8"))
    except FileNotFoundError:
        error(f"No se encontró {RUTA_PRODUCTOS}")
    except json.JSONDecodeError as exc:
        error(f"productos.json tiene JSON inválido: {exc}")


def guardar_productos(lista: list[dict]) -> None:
    texto = json.dumps(lista, ensure_ascii=False, indent=2) + "\n"
    RUTA_PRODUCTOS.write_text(texto, encoding="utf-8")


# -------------------------------------------------------------
# Imágenes (requiere Pillow)
# -------------------------------------------------------------
def _requiere_pillow() -> None:
    if Image is None:
        error("Falta Pillow. Instálalo con:  pip install -r herramientas/requirements.txt")


def optimizar_imagen(origen: Path, destino: Path, ancho: int, alto: int, max_kb: int) -> int:
    """Recorta al centro, reescala y comprime un JPEG hasta max_kb. Devuelve el peso final."""
    _requiere_pillow()
    imagen = Image.open(origen).convert("RGB")

    # Recorte centrado a la proporción pedida
    proporcion_objetivo = ancho / alto
    w, h = imagen.size
    proporcion_actual = w / h
    if proporcion_actual > proporcion_objetivo:  # imagen más ancha
        nuevo_w = round(h * proporcion_objetivo)
        x = (w - nuevo_w) // 2
        imagen = imagen.crop((x, 0, x + nuevo_w, h))
    elif proporcion_actual < proporcion_objetivo:  # imagen más alta
        nuevo_h = round(w / proporcion_objetivo)
        y = (h - nuevo_h) // 2
        imagen = imagen.crop((0, y, w, y + nuevo_h))
    imagen = imagen.resize((ancho, alto), Image.LANCZOS)

    # Búsqueda binaria de calidad: la mayor calidad que no supere max_kb
    mejor: bytes | None = None
    bajo, alto_q = 30, 92
    while bajo <= alto_q:
        calidad = (bajo + alto_q) // 2
        bufer = io.BytesIO()
        imagen.save(bufer, "JPEG", quality=calidad, optimize=True, progressive=True)
        if bufer.tell() <= max_kb * 1024:
            mejor = bufer.getvalue()
            bajo = calidad + 1
        else:
            alto_q = calidad - 1
    if mejor is None:  # incluso a calidad 30 pesa demasiado: se acepta tal cual
        bufer = io.BytesIO()
        imagen.save(bufer, "JPEG", quality=30, optimize=True, progressive=True)
        mejor = bufer.getvalue()

    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_bytes(mejor)
    return len(mejor)


def generar_portada(destino: Path, titulo_noticia: str) -> int:
    """Crea una portada decorativa (gradiente neón de la marca) cuando no hay foto."""
    _requiere_pillow()
    ancho, alto = PORTADA_ANCHO, PORTADA_ALTO
    imagen = Image.new("RGB", (ancho, alto), (11, 11, 20))
    dibujo = ImageDraw.Draw(imagen)
    dibujo.ellipse((-350, -350, 450, 450), fill=(0, 240, 255))          # halo cian
    dibujo.ellipse((ancho - 450, alto - 450, ancho + 350, alto + 350), fill=(255, 46, 209))
    imagen = imagen.filter(ImageFilter.GaussianBlur(200))

    oscura = Image.new("RGB", (ancho, alto), (11, 11, 20))
    imagen = Image.blend(imagen, oscura, 0.6)

    dibujo = ImageDraw.Draw(imagen)
    try:  # texto opcional: solo si Pillow permite fuentes escalables
        fuente = ImageFont.load_default(72)
        dibujo.text((ancho // 2, alto // 2), titulo_noticia.upper()[:28],
                    font=fuente, fill=(235, 235, 250), anchor="mm")
    except Exception:
        pass  # portada solo decorativa

    destino.parent.mkdir(parents=True, exist_ok=True)
    bufer = io.BytesIO()
    imagen.save(bufer, "JPEG", quality=80, optimize=True, progressive=True)
    destino.write_bytes(bufer.getvalue())
    return len(bufer.getvalue())


def peso_legible(bytes_: int) -> str:
    return f"{bytes_ / 1024:.0f} KB"


# -------------------------------------------------------------
# Comando: alta-producto
# -------------------------------------------------------------
def cmd_alta_producto(args: argparse.Namespace, simular: bool) -> None:
    titulo("Alta de producto")

    nombre = args.nombre or preguntar("Nombre del producto")
    producto_id = slugify(nombre)
    productos = cargar_productos()
    if any(p["id"] == producto_id for p in productos):
        error(f"Ya existe un producto con id «{producto_id}». Cambia el nombre.")

    categoria = args.categoria or preguntar_opcion("Categoría", CATEGORIAS)
    descripcion = args.descripcion or preguntar("Descripción (1-2 líneas)")
    destacado = True if args.destacado else preguntar_sino("¿Destacado en la portada?", False)
    foto = args.foto or preguntar_ruta("Ruta de la foto del producto (jpg/png/webp)")

    ruta_foto = Path(foto).expanduser()
    if not ruta_foto.is_file():
        error(f"No existe la foto: {ruta_foto}")
    destino_foto = DIR_FOTOS / f"{producto_id}.jpg"

    destacados_actuales = sum(1 for p in productos if p.get("destacado"))
    if destacado and destacados_actuales >= 3:
        aviso(f"Ya hay {destacados_actuales} productos destacados; la portada los mostrará todos.")

    print(f"\n{NEGRITA}Resumen:{RESET}")
    print(f"  id:          {MAGENTA}{producto_id}{RESET}")
    print(f"  nombre:      {nombre}")
    print(f"  categoría:   {categoria}")
    print(f"  destacado:   {'sí' if destacado else 'no'}")
    print(f"  foto →       {destino_foto.relative_to(RAIZ)} (800×800, máx {FOTO_MAX_KB} KB)")

    if simular:
        aviso("Modo simulación: no se escribió ningún archivo.")
        return

    peso = optimizar_imagen(ruta_foto, destino_foto, FOTO_ANCHO, FOTO_ALTO, FOTO_MAX_KB)
    productos.append({
        "id": producto_id,
        "nombre": nombre,
        "categoria": categoria,
        "descripcion": descripcion,
        "destacado": destacado,
    })
    guardar_productos(productos)

    ok(f"Foto optimizada: {peso_legible(peso)}")
    ok(f"Producto agregado a productos.json ({len(productos)} en total)")
    print(f"  {GRIS}Vista previa local:  python gestor.py publicar  → o abre /catalogo/{producto_id}/{RESET}")


# -------------------------------------------------------------
# Comando: alta-noticia
# -------------------------------------------------------------
def cmd_alta_noticia(args: argparse.Namespace, simular: bool) -> None:
    titulo("Alta de noticia")

    titulo_noticia = args.titulo or preguntar("Título de la noticia")
    noticia_id = slugify(titulo_noticia)
    ruta_noticia = DIR_NOTICIAS / f"{noticia_id}.md"
    if ruta_noticia.exists():
        error(f"Ya existe una noticia con id «{noticia_id}». Cambia el título.")

    descripcion = args.descripcion or preguntar("Descripción corta (aparece en el listado)")
    etiqueta = args.etiqueta or preguntar("Etiqueta (opcional, Enter para omitir)", "")
    fecha = args.fecha or preguntar("Fecha", defecto=date.today().isoformat())
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fecha):
        error("La fecha debe tener el formato AAAA-MM-DD.")

    cuerpo = leer_cuerpo(Path(args.cuerpo) if args.cuerpo else None)
    if not cuerpo:
        error("El cuerpo de la noticia quedó vacío.")

    portada = Path(args.portada).expanduser() if args.portada else None
    if portada and not portada.is_file():
        error(f"No existe la portada: {portada}")
    destino_portada = DIR_PORTADAS / f"{noticia_id}.jpg"

    print(f"\n{NEGRITA}Resumen:{RESET}")
    print(f"  id:          {MAGENTA}{noticia_id}{RESET}")
    print(f"  título:      {titulo_noticia}")
    print(f"  fecha:       {fecha}" + (f"   etiqueta: {etiqueta}" if etiqueta else ""))
    print(f"  archivo →    {ruta_noticia.relative_to(RAIZ)}")
    print(f"  portada →    {destino_portada.relative_to(RAIZ)} "
          f"({'tu foto' if portada else 'generada con el estilo de la marca'})")

    if simular:
        aviso("Modo simulación: no se escribió ningún archivo.")
        return

    frontmatter = [
        "---",
        f'titulo: "{escapar_yaml(titulo_noticia)}"',
        f"fecha: {fecha}",
    ]
    if etiqueta:
        frontmatter.append(f'etiqueta: "{escapar_yaml(etiqueta)}"')
    frontmatter.append(f'descripcion: "{escapar_yaml(descripcion)}"')
    frontmatter.append("---")
    ruta_noticia.parent.mkdir(parents=True, exist_ok=True)
    ruta_noticia.write_text("\n".join(frontmatter) + "\n\n" + cuerpo + "\n", encoding="utf-8")

    if portada:
        peso = optimizar_imagen(portada, destino_portada, PORTADA_ANCHO, PORTADA_ALTO, PORTADA_MAX_KB)
        ok(f"Portada optimizada: {peso_legible(peso)}")
    else:
        peso = generar_portada(destino_portada, titulo_noticia)
        ok(f"Portada decorativa generada: {peso_legible(peso)} (reemplázala luego si quieres)")

    ok(f"Noticia creada: {ruta_noticia.name}")


# -------------------------------------------------------------
# Comando: listar
# -------------------------------------------------------------
def _frontmatter_noticia(ruta: Path) -> dict:
    texto = ruta.read_text(encoding="utf-8")
    bloque = re.match(r"^---\n(.*?)\n---", texto, re.DOTALL)
    datos: dict = {}
    if bloque:
        for linea in bloque.group(1).splitlines():
            if ":" in linea:
                clave, _, valor = linea.partition(":")
                datos[clave.strip()] = valor.strip().strip('"')
    return datos


def cmd_listar(_args: argparse.Namespace, _simular: bool) -> None:
    titulo("Productos del catálogo")
    productos = cargar_productos()
    for categoria in CATEGORIAS:
        grupo = [p for p in productos if p["categoria"] == categoria]
        if not grupo:
            continue
        print(f"\n  {MAGENTA}{categoria}{RESET}")
        for p in grupo:
            foto_ok = "foto ✓" if (DIR_FOTOS / f"{p['id']}.jpg").is_file() else "foto ✗ FALTA"
            estrella = f"{AMARILLO}★{RESET} " if p.get("destacado") else "  "
            print(f"  {estrella}{p['id']} — {p['nombre']} {GRIS}({foto_ok}){RESET}")

    titulo("Noticias del blog")
    noticias = sorted(DIR_NOTICIAS.glob("*.md"), key=lambda r: _frontmatter_noticia(r).get("fecha", ""), reverse=True)
    if not noticias:
        print(f"  {GRIS}(sin noticias){RESET}")
    for noticia in noticias:
        datos = _frontmatter_noticia(noticia)
        portada_ok = "portada ✓" if (DIR_PORTADAS / f"{noticia.stem}.jpg").is_file() else "portada ✗"
        print(f"  {datos.get('fecha', '????-??-??')} — {datos.get('titulo', noticia.stem)} {GRIS}({portada_ok}){RESET}")


# -------------------------------------------------------------
# Comando: validar
# -------------------------------------------------------------
def cmd_validar(_args: argparse.Namespace, _simular: bool) -> None:
    titulo("Validación del contenido")
    problemas: list[str] = []

    productos = cargar_productos()
    ids = [p["id"] for p in productos]
    ok(f"productos.json: {len(productos)} productos, JSON válido")

    if len(ids) != len(set(ids)):
        duplicados = {i for i in ids if ids.count(i) > 1}
        problemas.append(f"IDs de producto duplicados: {sorted(duplicados)}")

    for p in productos:
        if not p.get("nombre") or not p.get("descripcion"):
            problemas.append(f"«{p['id']}»: nombre o descripción vacíos")
        if p.get("categoria") not in CATEGORIAS:
            problemas.append(f"«{p['id']}»: categoría inválida ({p.get('categoria')!r})")
        if not (DIR_FOTOS / f"{p['id']}.jpg").is_file():
            problemas.append(f"«{p['id']}»: falta la foto public/images/productos/{p['id']}.jpg")

    noticias = list(DIR_NOTICIAS.glob("*.md"))
    ok(f"noticias: {len(noticias)} entradas .md")
    for noticia in noticias:
        datos = _frontmatter_noticia(noticia)
        for campo in ("titulo", "fecha", "descripcion"):
            if campo not in datos:
                problemas.append(f"{noticia.name}: falta el campo «{campo}»")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", datos.get("fecha", "")):
            problemas.append(f"{noticia.name}: fecha inválida ({datos.get('fecha')!r})")
        if not (DIR_PORTADAS / f"{noticia.stem}.jpg").is_file():
            problemas.append(f"{noticia.name}: falta la portada public/images/blog/{noticia.stem}.jpg")

    if problemas:
        error(f"{len(problemas)} problema(s) encontrado(s):", salir=False)
        for problema in problemas:
            print(f"    - {problema}")
        sys.exit(1)
    ok("Todo el contenido está consistente. Listo para publicar.")


# -------------------------------------------------------------
# Comando: publicar
# -------------------------------------------------------------
def _git(*argumentos: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *argumentos], cwd=RAIZ, capture_output=True, text=True)


def cmd_publicar(args: argparse.Namespace, simular: bool) -> None:
    titulo("Publicar cambios")
    if not _git("rev-parse", "--is-inside-work-tree").returncode == 0:
        error("Esta carpeta no es un repositorio Git.")

    estado = _git("status", "--porcelain").stdout.strip()
    if not estado:
        ok("No hay cambios por publicar.")
        return

    print("  Cambios detectados:")
    for linea in estado.splitlines():
        print(f"    {GRIS}{linea}{RESET}")

    mensaje = args.mensaje or "Contenido: actualización de catálogo y noticias"
    if simular:
        aviso(f"Modo simulación: se haría commit «{mensaje}» y push.")
        return

    if not preguntar_sino("¿Confirmas publicar?", True):
        aviso("Cancelado. Nada se publicó.")
        return

    for paso in (["add", "-A"], ["commit", "-m", mensaje], ["push"]):
        resultado = _git(*paso)
        if resultado.returncode != 0:
            error(f"Falló git {paso[0]}:\n{resultado.stderr.strip()}")
        if paso[0] == "push":
            print(resultado.stdout.strip() or "  (repositorio actualizado)")

    ok("Publicado. El sitio se actualiza solo en ~2 minutos.")


# -------------------------------------------------------------
# Interfaz de línea de comandos
# -------------------------------------------------------------
def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="gestor.py",
        description="Mini-CMS para el sitio de Artesanía Tauro, C.A. (catálogo y noticias).",
        epilog=(
            "Ejemplos:\n"
            "  python gestor.py alta-producto\n"
            "  python gestor.py alta-noticia --cuerpo articulo.txt --portada foto.jpg\n"
            "  python gestor.py listar\n"
            "  python gestor.py validar\n"
            "  python gestor.py publicar --mensaje \"Nuevos productos de temporada\"\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--simular", action="store_true",
                        help="muestra qué haría el comando sin escribir archivos")
    sub = parser.add_subparsers(dest="comando", required=True)

    p_prod = sub.add_parser("alta-producto", help="agrega un producto con foto optimizada")
    p_prod.add_argument("--nombre", help="nombre del producto")
    p_prod.add_argument("--categoria", choices=CATEGORIAS, help="categoría del catálogo")
    p_prod.add_argument("--descripcion", help="descripción corta")
    p_prod.add_argument("--foto", help="ruta de la foto (se optimiza automáticamente)")
    p_prod.add_argument("--destacado", action="store_true", help="mostrar en la portada")

    p_not = sub.add_parser("alta-noticia", help="agrega una entrada al blog")
    p_not.add_argument("--titulo", help="título de la noticia")
    p_not.add_argument("--descripcion", help="resumen para el listado")
    p_not.add_argument("--etiqueta", help="etiqueta opcional (Consejos, Colecciones, Eventos...)")
    p_not.add_argument("--fecha", help="fecha AAAA-MM-DD (por defecto: hoy)")
    p_not.add_argument("--cuerpo", help="archivo .txt/.md con el artículo (si no, se pide por teclado)")
    p_not.add_argument("--portada", help="foto de portada (si no, se genera una decorativa)")

    sub.add_parser("listar", help="muestra productos y noticias actuales")
    sub.add_parser("validar", help="revisa consistencia de datos e imágenes")

    p_pub = sub.add_parser("publicar", help="commit + push hacia el sitio en línea")
    p_pub.add_argument("--mensaje", help="mensaje del commit")
    return parser


def main() -> None:
    parser = construir_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        return
    args = parser.parse_args()
    comandos = {
        "alta-producto": cmd_alta_producto,
        "alta-noticia": cmd_alta_noticia,
        "listar": cmd_listar,
        "validar": cmd_validar,
        "publicar": cmd_publicar,
    }
    try:
        comandos[args.comando](args, args.simular)
    except (KeyboardInterrupt, EOFError):
        print()
        aviso("Cancelado.")


if __name__ == "__main__":
    main()
