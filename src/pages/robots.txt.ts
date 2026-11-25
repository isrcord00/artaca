// =============================================================
// robots.txt dinámico — toma la URL configurada en `site`
// (astro.config.mjs) para apuntar siempre al sitemap correcto.
// Sustituye al archivo estático public/robots.txt.
// =============================================================
import type { APIRoute } from 'astro';

export const GET: APIRoute = ({ site }) => {
  const sitemap = site ? new URL('sitemap-index.xml', site).href : '/sitemap-index.xml';

  const cuerpo = [
    '# Permitimos el rastreo completo a todos los buscadores',
    'User-agent: *',
    'Allow: /',
    '',
    '# Mapa del sitio generado por Astro (@astrojs/sitemap)',
    `Sitemap: ${sitemap}`,
    '',
  ].join('\n');

  return new Response(cuerpo, {
    headers: { 'Content-Type': 'text/plain; charset=utf-8' },
  });
};
