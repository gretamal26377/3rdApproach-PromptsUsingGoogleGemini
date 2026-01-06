// import React from "react";
import ReactDOMServer from "react-dom/server";
import { StaticRouter } from "react-router-dom/server";
import { AuthProvider } from "shared-lib";
// import App from "../App";
import { escapeInject, dangerouslySkipEscape } from "vite-plugin-ssr/server";
import "../../../globals.css";

export { render };

/**
 * @param {Record<string, any>} pageContext
 */
function render(pageContext) {
  // pageContext.Page get its value from index.page.jsx (This case: App component)
  const Page = pageContext.Page;
  const appHtml = ReactDOMServer.renderToString(
    <StaticRouter location={pageContext.urlOriginal}>
      <AuthProvider>
        <Page />
      </AuthProvider>
    </StaticRouter>
  );
  return escapeInject`<!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="UTF-8" />
        <title>SSR App</title>
      </head>
      <body>
        {/* When doing SSR, the content is injected raw, unescaped HTML, so browser sees a valid DOM structure,
            not the literal source code. That's the reason this function skips escaping */}
        <div id="root">${dangerouslySkipEscape(appHtml)}</div>
      </body>
    </html>`;
}
