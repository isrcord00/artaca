// @ts-check
// =============================================================
// Configuración de Astro — Sitio «Artesanía Tauro, C.A.»
// -------------------------------------------------------------
// - Tailwind CSS v4 se integra como plugin de Vite.
// - `site` se actualizará con el dominio final del cliente
//   cuando contrate hosting propio (ver plan.md, fase F6).
// =============================================================
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  // URL pública del sitio (subdominio demo de Cloudflare Pages;
  // se actualizará al dominio final cuando el cliente lo contrate)
  site: 'https://artaca.pages.dev',

  // Integraciones: sitemap.xml automático para buscadores
  integrations: [sitemap()],

  // Plugins de Vite: procesamiento de Tailwind CSS
  vite: {
    plugins: [tailwindcss()],
  },
});
