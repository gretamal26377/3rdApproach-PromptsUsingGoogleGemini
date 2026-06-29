# Copilot AI Coding Agent Instructions

## Project Overview

This monorepo contains a Marketplace Application with a microservices-inspired structure:

- **backend/**: Python Flask (Customer, Organisation-Admin and Platform-Admin App APIs, SQLAlchemy models, ERD scripts)
- **frontend/**: React (Customer, Organisation-Admin, Platform-Admin Apps, shared-lib)
- **database/**: SQL scripts and Docker Compose for DB setup

## Key Architectural Patterns

- **Backend**: Modular Flask apps for Customer, Organisation-Admin and Platform-Admin Apps, each with their own `create_app()` in `app.org_admin`, `app.platform_admin`, and `app.customer`. Shared models and DB logic live in `app.shared`.
- **Frontend**: Each frontend (Customer, Organisation-Admin and Platform-Admin) is a separate React App, with a shared component library (`shared-lib`).
- **Database**: Managed via SQL scripts and Docker Compose. Models are defined in Python and can be auto-documented with ERD scripts.

## Developer Workflows

- **Backend**:
  - Use `python -m scripts.generate_er_diagram` to generate ER diagrams (requires Graphviz and eralchemy2).
  - Run all unittests: `python -m unittest discover -s pwa-marketplace/backend/tests -p '*_test.py' -v`
  - Use the correct `create_app()` import: `from app.org_admin import create_app` for org_admin,  `from app.platform_admin import create_app` for platform_admin and `from app.customer import create_app` for customer.
- **Frontend**:
  - Each app (`org_admin`, `platform_admin`, `customer`, `shared-lib`) has its own `package.json` and build process.
  - Use Storybook for UI development in `shared-lib`.
- **Database**:
  - Start with Docker Compose in `database/`.
  - Use `init.sql` for schema setup.

## Frontend Component Consistency Rules

- For any frontend component creation, modification, or refactor, you must:
  - Check and follow all directives in `STYLEGUIDE.md` to ensure consistency with the project's look & feel.
  - Use and prefer UI primitives from the `frontend/shared-lib/src/components/ui/` folder whenever possible, instead of creating new base components or duplicating styles.
  - Only introduce new UI primitives if there is no suitable existing component, and update `STYLEGUIDE.md` accordingly.

### Dropdowns and Checkboxes: Animation & Accessibility

- All dropdowns must use smooth open/close animation (opacity, scale) and support keyboard navigation (Tab, Arrow keys, Enter/Space).
- All dropdowns must use ARIA roles (`listbox`, `option`, `aria-expanded`, `aria-controls`) and trap focus when open.
- All checkboxes must have visible focus outlines, ARIA attributes, and animated checkmark feedback.
- Use shared UI primitives for dropdowns and checkboxes to ensure these features are applied project-wide.

## Project-Specific Conventions

If form validation fails, display a clear error message (e.g., Alert or FormMessage).
Do NOT clear or reset the form or its input values on validation failure.
Keep all user input intact so the user can immediately fix any wrong or incomplete fields and resubmit.
Only calls form.reset() after successful create/update.
This applies to all forms (signup, login, checkout, etc.) in both admin and customer apps.

- **No global `create_app()` in `app/__init__.py` by default**; import from the relevant submodule.
- **Shared code** (models, DB logic) lives in `app/shared/`.
- **Scripts** (like ERD generation) may need to adjust their `create_app` import depending on which app context is required.
- **Frontend shared-lib** is used by all admin and customer frontends; keep components generic.
- **Dockerfiles** and `docker-compose.yml` files are present for both backend and frontend, supporting local and containerized workflows.

## Integration Points

- **Backend/Frontend**: Communicate via REST APIs.
- **Backend/Database**: SQLAlchemy ORM, DB config via environment variables or `.env` files.
- **Frontend/Shared-lib**: Import shared components/utilities from `shared-lib`.

## Examples

- To generate an ER diagram for the Organisation-Admin backend:
  ```python
  from app.org_admin import create_app
  # ...
  ```
- To run all backend tests:
  ```sh
  python -m unittest discover -s pwa-marketplace/backend/tests -p '*_test.py' -v
  ```
- To start the database (GRL: Not sure about it):
  ```sh
  cd database
  docker-compose up -d
  ```

## References

- See `README.md` in each major directory for more details.
- For Storybook usage, see `frontend/shared-lib/src/stories/Configure.mdx`.

---

**If you are unsure which `create_app()` to use, check the script's context or ask for clarification**
