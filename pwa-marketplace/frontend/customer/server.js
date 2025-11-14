import express from "express";
import { createServer as createViteServer } from "vite";
import fs from "fs";
import path from "path";

async function startServer() {
  const app = express();
  const vite = await createViteServer({
    server: { middlewareMode: "ssr" },
    // This server doesn't fit other choices such as: vue3, angular, etc. So it's set to custom
    appType: "custom",
  });

  // use vite's connect instance as middleware
  app.use(vite.middlewares);

  // Sets up a "catch-all" middleware function that will run for every single HTTP request your server receives
  // async allows using await inside the function
  app.use("*", async (req, res) => {
    const url = req.originalUrl;
    // Read index.html
    let template = fs.readFileSync(
      path.resolve(__dirname, "index.html"),
      "utf-8"
    );
    // Apply Vite HTML transforms. This injects the Vite HMR client, and
    // also applies HTML transforms from Vite plugins, e.g. global preambles
    template = await vite.transformIndexHtml(url, template);
    // { render }: Destructured function exported from entry-server.jsx
    const { render } = await vite.ssrLoadModule("/src/entry-server.jsx");
    const appHtml = render();
    // Inject the app-rendered HTML into the template
    const html = template.replace(`<!--app-html-->`, appHtml);
    // res: Express 'res'ponse object
    res.status(200).set({ "Content-Type": "text/html" }).end(html);
  });

  app.listen(3000, () => {
    console.log("SSR server running at http://localhost:3000");
  });
}

startServer();
