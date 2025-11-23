const express = require("express");
const { createPageRenderer } = require("vite-plugin-ssr");
const vite = require("vite");
const isProduction = process.env.NODE_ENV === "production";
const root = __dirname;

async function startServer() {
  const app = express();

  // --- Dynamic sitemap.xml Route ---
  app.get('/sitemap.xml', async (req, res) => {
    const baseUrl = process.env.BASE_URL || 'http://localhost:3000';
    // TODO: Fetch/generate all dynamic URLs (products, services, etc.)
    const urls = [
      `${baseUrl}/`,
      // Add more URLs dynamically here
    ];
    const xml = `<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n${urls.map(url => `<url><loc>${url}</loc></url>`).join('\n')}\n</urlset>`;
    res.header('Content-Type', 'application/xml');
    res.send(xml);
  });
  let viteDevServer;
  if (!isProduction) {
    viteDevServer = await vite.createServer({
      root,
      server: { middlewareMode: "ssr" },
    });
    app.use(viteDevServer.middlewares);
  } else {
    app.use(express.static(`${root}/dist/client`));
  }
  const renderPage = createPageRenderer({ viteDevServer, isProduction, root });
  app.get("*", async (req, res, next) => {
    const pageContextInit = { urlOriginal: req.originalUrl };
    const pageContext = await renderPage(pageContextInit);
    const { httpResponse } = pageContext;
    if (!httpResponse) return next();
    httpResponse.pipe(res);
  });

  app.listen(3000, () => {
    console.log("SSR server running at http://localhost:3000");
  });
}

startServer();
