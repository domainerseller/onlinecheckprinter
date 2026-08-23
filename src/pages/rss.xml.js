import rss from '@astrojs/rss';
import { getCollection } from 'astro:content';

export async function GET(context) {
  const articles = (await getCollection('articles', ({ data }) => !data.draft)).sort(
    (a, b) => b.data.pubDate.valueOf() - a.data.pubDate.valueOf()
  );

  return rss({
    title: 'OnlineCheckPrinter',
    description:
      'Independent reviews and guides on check-printing services and software for businesses. Compare cost, integrations, and fraud protection.',
    site: context.site,
    items: articles.map((article) => ({
      title: article.data.title,
      description: article.data.description,
      pubDate: article.data.pubDate,
      author: article.data.author,
      link: `/articles/${article.slug}/`,
      categories: article.data.tags,
    })),
    customData: `<language>en-us</language>`,
  });
}
