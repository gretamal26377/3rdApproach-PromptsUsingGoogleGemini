# CLAUDE.md — Project Context for AI Assistants

## What This Project Is

A **multi-vendor e-commerce marketplace platform** under active development. Multiple independent Stores, each belonging to an Organisation, can list Products and Services. Customers use the platform to search, browse, cart, checkout, and track orders — all through a single unified interface.

Think of it as a lightweight MercadoLibre or Etsy, with a full back-office for both organisation-level and platform-level administration.

---

## Who Uses It

Three distinct user audiences, each with their own dedicated frontend and backend app:

**Customers** — browse stores, search for products/services, manage a shopping cart, checkout, and view order history.

**Organisation Admins** — manage their organisation's stores, products/services, pricing, categories, and internal user roles (Admin, Supervisor, Staff, Viewer).

**Platform Admins** — oversee the entire platform from a bird's-eye view: all organisations, stores, users, and orders.

---

## User Roles (at Organisation level)

| Role       | Access                                      |
|------------|---------------------------------------------|
| Admin      | Full management power                       |
| Supervisor | Operational management                      |
| Staff      | Daily paperwork/task management             |
| Viewer     | Read-only, no modifications allowed         |

---

## Architecture Overview

A **microservices-inspired monorepo** split across three layers:

### Frontend — React + Vite
- Three separate React apps: `customer`, `org-admin`, `platform-admin`
- All share a common component library: `frontend/shared-lib`
- The customer app is a **PWA** with SSR support via `vite-plugin-ssr`
- Admin frontends are CSR only
- Styling: **Tailwind CSS** (utility-first, with custom design tokens)
- Form validation: **Zod + React Hook Form**
- Icons: **Lucide React**
- UI components: custom primitives in `shared-lib/src/components/ui/`

### Backend — Python Flask
- Three separate Flask apps: `customer`, `org_admin`, `platform_admin`
- Each has its own routes and business logic
- Shared code (models, DB, auth, utils) lives in `app/shared/`
- ORM: **SQLAlchemy** (managed via **Alembic** migrations)
- Search: **pluggable at Docker build time** — Meilisearch (default) or Google Search Engine
- Order state management: **Temporal Workflow Engine**

### Database — MySQL
- Single MySQL instance, managed via Docker
- Schema defined in `database/init.sql`
- Models in `backend/app/shared/models.py`

---

## Project Structure (abbreviated)

```
pwa-marketplace/
├── backend/
│   ├── app/
│   │   ├── admin/
│   │   ├── customer/
│   │   ├── org_admin/
│   │   ├── platform_admin/
│   │   └── shared/          ← shared models, auth, DB, utils, search
│   ├── alembic/             ← DB migrations
│   ├── docs/                ← ER diagrams
│   └── tests/
├── database/
│   ├── init.sql
│   └── Dockerfile
├── frontend/
│   ├── customer/            ← PWA + SSR React app
│   ├── org-admin/           ← CSR React app
│   ├── platform-admin/      ← CSR React app
│   └── shared-lib/          ← shared UI components and utilities
├── docker-compose.yml
├── STYLEGUIDE.md
├── CLAUDE.md                ← this file
└── README.md
```

---

## Key Architectural Decisions

### Monorepo with Shared Code
- `frontend/shared-lib` — shared React components, hooks, services, and UI primitives
- `backend/app/shared` — shared Flask models, DB config, auth, and utilities
- Each app remains independently deployable while avoiding duplication

### Pluggable Search Engine
Switched at Docker build time via a build argument:
```sh
docker build --build-arg SEARCH_ENGINE=meili -t backend:meili .
docker build --build-arg SEARCH_ENGINE=google -t backend:google .
```
All backend code imports from `app.shared.search` regardless of which engine is active.

### Order State Management
Uses **Temporal Workflow Engine** for resilient, long-running order flows with proper state transitions.

### create_app() Imports
Each Flask app has its own factory. Always import from the correct submodule:
```python
from app.org_admin import create_app       # for org-admin context
from app.platform_admin import create_app  # for platform-admin context
from app.customer import create_app        # for customer context
```
There is **no global** `create_app()` in `app/__init__.py`.

---

## Frontend Component Consistency Rules

- Always check and follow `STYLEGUIDE.md` before creating or modifying any frontend component
- Use and prefer UI primitives from `frontend/shared-lib/src/components/ui/` whenever possible
- Only introduce new UI primitives if no suitable component exists; update `STYLEGUIDE.md` accordingly
- All styling goes through **Tailwind CSS** — no custom CSS unless strictly necessary

### Available UI Primitives (shared-lib)
`Button`, `Input`, `Form`, `FormLabel`, `Table`, `TableHeader`, `TableBody`, `TableRow`, `TableHead`, `TableCell`, `Card`, `Alert`, `Badge`, `Carousel`, `Checkbox`, `Dialog`, `Dropdown`, `ScrollArea`, `ToggleSwitch`, `DarkModeToggle`

### Design Tokens (globals.css + tailwind.config.js)
| Token                  | Light Mode  | Dark Mode   |
|------------------------|-------------|-------------|
| `--color-background`   | `#e4e4e4`   | `#18181b`   |
| `--color-text`         | `#18181b`   | `#ffffff`   |

Custom Tailwind classes: `bg-background`, `text-text`, `dark:bg-background-dark`, `dark:text-text-dark`, `bg-primary`, `bg-secondary`, `bg-muted`, `bg-card`, `bg-input`, and their dark variants.

---

## Accessibility & Animation Rules

- All **dropdowns** must use smooth open/close animation (opacity + scale) and support keyboard navigation (Tab, Arrow keys, Enter/Space)
- All **dropdowns** must use ARIA roles: `listbox`, `option`, `aria-expanded`, `aria-controls`, and trap focus when open
- All **checkboxes** must have visible focus outlines, ARIA attributes, and animated checkmark feedback
- Use `shared-lib` primitives for dropdowns and checkboxes to enforce these rules project-wide

---

## Form Validation UX Rules

These apply to **all** forms across all apps (signup, login, checkout, product management, etc.):

- On validation failure: show a clear error message (`Alert` or `FormMessage`)
- **Do NOT** clear or reset the form or its input values on failure
- Keep all user input intact so the user can fix and resubmit immediately
- Only call `form.reset()` after a **successful** create or update

---

## Developer Workflows

### Backend
```sh
# Run all tests
python -m unittest discover -s pwa-marketplace/backend/tests -p '*_test.py' -v

# Generate ER diagram
python -m scripts.generate_er_diagram
```

### Frontend
```sh
# Install dependencies (from frontend/)
pnpm install

# Run customer app (dev)
pnpm run dev

# Run Storybook (from shared-lib)
pnpm run storybook
```

### Database
```sh
cd database
docker-compose up -d
```

### Full Stack (Docker Compose)
```sh
docker compose up
# Customer frontend at http://localhost:3000
```

---

## Current Development Status

The project is under active development. The core architecture is established, but several areas are still being refined. Signs of iteration visible in the codebase include multiple model file variants (`models_*.py`), `*.old.*` files, `_copy` files, and notes marked `GRL: Need review & update`. These are intentional artifacts of an evolving design.

---

## References

- `STYLEGUIDE.md` — UI/UX conventions, Tailwind patterns, component rules
- `SEARCH_ENGINE_SWITCH.md` — how the pluggable search engine build arg works
- `backend/docs/ER_DIAGRAM_README.md` — ER diagram generation instructions
- `frontend/shared-lib/src/stories/` — Storybook component documentation
