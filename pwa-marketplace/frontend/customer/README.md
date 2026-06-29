# React + Vite (GRL: TBReviewed)

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project
<br>

### Commands to leverage use of Aliases

To use the src alias (development):  
_**npm run dev**_  
or  
_**vite**_

To use the dist alias (production build):  
_**npm run build**_  
or  
_**vite build**_

Definition/Explanation for this is in _**vite.config.js**_

## SSR with vite-plugin-ssr (Centralized Routing)

This app uses vite-plugin-ssr for SEO-friendly SSR, while keeping centralized routing (React Router in App.jsx/Routes.jsx).

### How it works

- SSR entry files are in `src/pages/`:
  - `_default.page.server.jsx` (SSR)
  - `_default.page.client.jsx` (hydration)
  - `index.page.jsx` (points to your App)
- Your existing App.jsx and Routes.jsx remain unchanged and manage all routes
- Service Worker registration and BrowserRouter are only used on the client
- StaticRouter is used on the server for SSR

### Development

```sh
pnpm install
pnpm run dev
```

### Production

```sh
pnpm run build
pnpm start
```

App runs at http://localhost:3000

### File Overview

- `index.html`: Contains `<div id="root"><!--app-html--></div>` for SSR injection
- `server.js`: SSR server (Express)
- `src/pages/_default.page.server.jsx`: SSR entry
- `src/pages/_default.page.client.jsx`: Hydration entry
- `src/pages/index.page.jsx`: Points to App.jsx (centralized routing)
- `App.jsx`, `Routes.jsx`: Your main app and routing logic (unchanged)

### Docker Compose (Recommended for full stack)

- The SSR server will run automatically on port 3000:
  ```sh
  docker compose up frontend-customer
  ```
  Then visit http://localhost:3000

### Notes

- Admin frontend remains CSR only
- shared-lib is used by both frontends
