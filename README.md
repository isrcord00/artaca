# Artesanía Tauro, C.A. — Sitio Web Demo

Sitio institucional **responsive** para **Artesanía Tauro, C.A.** (Barquisimeto, Lara, Venezuela):
venta al mayor y detal de calzado tejido artesanal — alpargatas, cocuizas y bolsos.

Proyecto demo para oferta en Workana + proyecto personal de portfolio.
Operación **100 % gratuita** (hosting, formulario y blog sin costo).

> 📋 El plan de trabajo completo (investigación, fases, design system) está en `../plan.md`.

## Stack

| Capa | Herramienta |
|---|---|
| Framework | [Astro](https://astro.build) |
| Estilos | [Tailwind CSS v4](https://tailwindcss.com) (plugin Vite) |
| Formulario | Web3Forms (integrado — configurar `PUBLIC_WEB3FORMS_KEY` en `.env`) |
| Blog | Colecciones Markdown de Astro (por integrar — F4) |
| Deploy | Cloudflare Pages (por configurar — F6) |

## Estilo: Dark Neon

Los tokens del design system están centralizados en `src/styles/global.css`
(dentro del bloque `@theme` de Tailwind v4):

- Fondo: `#0B0B14` · Superficies: `#12121F` / `#1A1B2E`
- Neones: cian `#00F0FF` · magenta `#FF2ED1` · violeta `#8A2BE2`
- Tipografías: **Orbitron** (títulos) e **Inter** (cuerpo), vía Google Fonts
- Efectos: glow, glassmorphism, rejilla de fondo, botones neón

## Cómo ejecutar el proyecto

```bash
# 1. Instalar dependencias
npm install

# 2. Servidor de desarrollo (http://localhost:4321)
npm run dev

# 3. Compilar para producción (salida en ./dist/)
npm run build

# 4. Previsualizar la compilación localmente
npm run preview
```

## Estructura del proyecto

```
artesania-tauro/
├── public/                  # Archivos estáticos (favicon, imágenes futuras)
├── src/
│   ├── components/          # Componentes reutilizables
│   │   ├── Header.astro     # Navegación responsive (CSS-only)
│   │   ├── Footer.astro     # Pie con datos de contacto reales
│   │   ├── Hero.astro       # Portada de inicio
│   │   ├── BotonNeon.astro  # Botón reutilizable (variantes neon/fantasma)
│   │   └── TarjetaProducto.astro
│   ├── data/
│   │   └── productos.json   # Catálogo de ejemplo (F3 lo ampliará)
│   ├── layouts/
│   │   └── Base.astro       # Layout con SEO, tipografías, header y footer
│   ├── pages/               # Rutas del sitio (enrutamiento por archivos)
│   │   ├── index.astro      # Inicio
│   │   ├── nosotros.astro   # (placeholder — F2)
│   │   ├── catalogo.astro   # (placeholder — F3)
│   │   ├── noticias.astro   # (placeholder — F4)
│   │   ├── contacto.astro   # (placeholder — F2)
│   │   └── 404.astro        # Página de error personalizada
│   └── styles/
│       └── global.css       # Tokens Dark Neon + utilidades de marca
├── astro.config.mjs
└── package.json
```

## Estado del proyecto

- [x] **F0** — Setup del proyecto (Astro + Tailwind)
- [x] **F1** — Design system Dark Neon + componentes base + página demo
- [x] **F2** — Páginas core: Nosotros, Contacto (formulario funcional)

> 🔑 **Para activar el formulario:** copia `.env.example` como `.env`, crea una clave
> gratuita en [web3forms.com](https://web3forms.com) (con el correo del cliente) y pégala
> en `PUBLIC_WEB3FORMS_KEY`. El archivo `.env` no se sube al repositorio.
- [ ] **F3** — Catálogo completo con filtros
- [ ] **F4** — Blog/Noticias con Markdown y RSS
- [ ] **F5** — SEO avanzado (Open Graph, sitemap, schema LocalBusiness)
- [ ] **F6** — Deploy en Cloudflare Pages
- [ ] **F7** — QA responsive + Lighthouse
- [ ] **F8** — Presentación al cliente

## Convenciones

- **Todo el código, comentarios y documentación están en español.**
- Los datos de contacto provienen de la investigación web (ver `../plan.md`)
  y deben confirmarse con el cliente antes de la entrega final.
- Las imágenes de productos son placeholders: se reemplazarán por fotos reales.
