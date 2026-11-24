// =============================================================
// Configuración de colecciones de contenido.
// «noticias»: entradas del blog escritas en Markdown dentro de
// src/content/noticias/ (una noticia = un archivo .md).
// =============================================================
import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const noticias = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/noticias' }),
  schema: z.object({
    titulo: z.string(),
    fecha: z.coerce.date(),
    descripcion: z.string(),
    etiqueta: z.string().optional(),
  }),
});

export const collections = { noticias };
