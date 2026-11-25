# Guía de Despliegue — Cloudflare Pages (gratis)

Puesta en línea del sitio **Artesanía Tauro, C.A.** sin costo, con HTTPS
y dominio demo incluido. Tiempo estimado: **15 minutos**.

> **Estado:** ✅ desplegado en **https://artaca.isrcordigital.top** — se usó el
> flujo nuevo **Workers Builds** (config en `wrangler.jsonc`, assets estáticos)
> con un dominio propio administrado en Cloudflare. La guía clásica de Pages
> aquí abajo sigue siendo válida como alternativa.

---

## Paso 1 — Subir el código a GitHub ✅ (hecho)

Repositorio ya publicado en: **https://github.com/isrcord00/artaca**

## Paso 2 — Crear el proyecto en Cloudflare Pages

1. Crea una cuenta gratis en https://dash.cloudflare.com (sign-up).
2. Ve a **Workers & Pages → Create → Pages → Connect to Git**.
3. Autoriza GitHub y selecciona el repositorio `artaca`.

## Paso 3 — Configuración de compilación

| Campo | Valor |
|---|---|
| Framework preset | **Astro** |
| Build command | `npm run build` |
| Build output directory | `dist` |

## Paso 4 — Variable de entorno del formulario

En **Settings → Environment variables**, agrega (para *Production* y *Preview*):

| Nombre | Valor |
|---|---|
| `PUBLIC_WEB3FORMS_KEY` | tu access key de https://web3forms.com |
| `NODE_VERSION` | `20` |

> ⚠️ Importante: crea la clave de Web3Forms con el **correo del cliente**
> para que los mensajes le lleguen directamente a su casilla.
> `NODE_VERSION=20` garantiza que el build use una versión moderna de Node.

## Paso 5 — ¡Desplegar!

Presiona **Save and Deploy**. En ~2 minutos el sitio estará en línea en:

```
https://artaca.pages.dev
```

Cada `git push` a `main` actualizará el sitio automáticamente.

---

## Dominio propio (opcional, lo paga el cliente)

Cuando el cliente compre su dominio (ej. `artesaniatauro.com.ve`, ~USD 10/año):

1. En Cloudflare Pages: **Custom domains → Set up a domain**.
2. Agrega el dominio y sigue los pasos para apuntar los DNS.
3. Actualiza `site` en `astro.config.mjs` con el dominio final y vuelve a
   desplegar (esto regenera el sitemap y las URLs canónicas).

## Alternativas gratuitas equivalentes

- **Netlify**: mismo proceso (conecta repo, build `npm run build`, output `dist`).
- **Vercel**: ídem.
- **GitHub Pages**: posible, pero requiere configurar `base` en Astro si el
  sitio no va en la raíz del dominio.

## Verificación post-despliegue (checklist)

- [ ] Inicio, catálogo (filtros), noticias y contacto cargan bien
- [ ] El formulario envía y llega el correo de prueba
- [ ] `https://…/rss.xml` responde
- [ ] `https://…/sitemap-index.xml` responde
- [ ] Compartir la URL en WhatsApp/Facebook muestra el título y descripción (Open Graph)
- [ ] Probar en un teléfono real (responsive)
