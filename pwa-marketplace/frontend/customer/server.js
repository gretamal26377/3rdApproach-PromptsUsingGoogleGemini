const express = require("express");
const { createPageRenderer } = require("vite-plugin-ssr");
const vite = require("vite");
const isProduction = process.env.NODE_ENV === "production";
const root = __dirname;

async function startServer() {
  const app = express();
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
