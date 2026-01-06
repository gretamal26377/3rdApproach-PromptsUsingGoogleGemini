// express: Simple SSR server with dynamic sitemap.xml route
import express from "express";
import { createPageRenderer } from "vite-plugin-ssr";
import { createServer } from "vite";
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const isProduction = process.env.NODE_ENV === "production";
const __filename = fileURLToPath(import.meta.url);
const root = dirname(__filename);

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
    viteDevServer = await createServer({
      root,
      // server: { middlewareMode: "ssr" },
      server: { middlewareMode: true },
    });
    app.use(viteDevServer.middlewares);
  } else {
    // In production, serve the pre-built static files from the dist/client directory
    app.use(express.static(`${root}/dist/client`));
  }
  const renderPage = createPageRenderer({ viteDevServer, isProduction, root });
  // --- SSR Express server listen for all routes ---
  app.get("*", async (req, res, next) => {
    const pageContextInit = { urlOriginal: req.originalUrl };
    // For each request, it calls renderPage from vite-plugin-ssr to handle SSR, passing {urlOriginal: req.originalUrl}
    // vite-plugin-ssr matches `/` to index.page.jsx derived from: vite.config.js to search from 'src/pages'
    // vite-plugin-ssr automatically search for files named *.page.jsx or *.page.server.jsx in 'src/pages' directory
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
