# React + Vite

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

## SSR (Server-Side Rendering) Setup

This app is now configured for SEO-friendly SSR using Vite SSR and Express

### Local Development (SSR)

1. Install dependencies and build shared-lib:
   ```sh
   cd ../../shared-lib
   npm install
   npm run build
   ```
2. Install dependencies for customer frontend:
   ```sh
   cd ../customer
   npm install
   ```
3. Start the SSR server:
   ```sh
   node server.js
   ```
   The app will be available at http://localhost:3000

### Docker Compose (Recommended for full stack)

- The SSR server will run automatically on port 3000:
  ```sh
  docker compose up frontend-customer
  ```
  Then visit http://localhost:3000

### How it works

- On each request, the server renders the app to HTML (SSR) and sends it to the browser
- The browser hydrates the app for full interactivity (CSR)
- All code and components are shared between SSR and CSR entry points

### File Overview

- `server.js`: Express SSR server
- `src/entry-server.jsx`: Server-side entry (for SSR)
- `src/entry-client.jsx`: Client-side entry (for hydration)
- `index.html`: Contains `<div id="root"><!--app-html--></div>` for SSR injection

### Notes

- Admin frontend remains CSR only
- shared-lib is used by both frontends
