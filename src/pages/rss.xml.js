// =============================================================
// Canal RSS de noticias — /rss.xml
// Permite que clientes y tiendas se suscriban a las novedades.
// =============================================================
import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  const noticias = await getCollection('noticias');

  return rss({
    title: 'Noticias — Artesanía Tauro, C.A.',
    description:
      'Novedades, colecciones y consejos del taller de calzado tejido artesanal Artesanía Tauro, C.A. (Barquisimeto, Venezuela).',
    site: context.site,
    items: noticias.map((entrada) => ({
      title: entrada.data.titulo,
      pubDate: entrada.data.fecha,
      description: entrada.data.descripcion,
      link: `/noticias/${entrada.id}/`,
    })),
    customData: '<language>es-VE</language>',
  });
}
