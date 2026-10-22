# Plan: audit the draft AGENTS.md and propose a corrected one

## Files that would be modified (scope)
- **`pwa-marketplace/AGENTS.md`** — rewritten (section 6). Always.
- **`pwa-marketplace/CLAUDE.md`** — only the small fixes in section 7, and only if you approve them.
- **Nothing else.** The bugs found in section 3-5 (auth.py, models.py, init.sql, Alembic, docker-compose, workflows, frontend, README, STYLEGUIDE) are **reported, not fixed**. AGENTS.md just lists them under "Known issues" so agents don't trust them.
- No commit and no push.

## Context
`pwa-marketplace/AGENTS.md` (untracked) was drafted to hold the team structure, access policy, security checklist and end-of-task report format. CLAUDE.md is treated as settled. Three read-only audits compared the draft with the real codebase. Nothing has been edited. Line numbers below come from those audits; items marked (unverified) were inferred from reading code, not run.

Paths are relative to `pwa-marketplace/` unless noted. Spot-checked by me directly: `shared/management.py` is missing, `auth.py:5` imports it, `create_app` exists in `app/__init__.py`, `init.sql` has no seed rows, and `init copy.sql` differs from `init.sql` only in comments.

## 0. Biggest problem with the draft itself
- `AGENTS.md` is an older copy of CLAUDE.md (title still says "CLAUDE.md"). Line 15 is `@AGENTS.md`, so it imports itself.
- It contains none of the promised sections (team structure, access policy, security checklist, report format).
- The current CLAUDE.md on disk has no `@AGENTS.md` import and no "Agent Teams" section, so the two files are out of sync in both directions.
- CLAUDE.md's Self-Maintenance Rule (line 233-236) says to append to a `## Changelog` section that does not exist.

## 1. Wrong paths and claims in the draft
| Draft says | Reality |
|---|---|
| `database/init.sql` (L66, L85) | `database/docker-entrypoint-initdb.d/init.sql` |
| `SEARCH_ENGINE_SWITCH.md` (L215) | `backend/SEARCH_ENGINE_SWITCH.md` |
| "There is no global `create_app()` in `app/__init__.py`" (L125) | It exists (`app/__init__.py:9`) but is a bare stub. `platform_admin` has no `create_app` and no `wsgi.py` |
| `docker build --build-arg SEARCH_ENGINE=...` on the default Dockerfile | Only `Dockerfile-search` has the arg (`-f Dockerfile-search`). The result lands in `/app/search`, not `app/shared/search` |
| `cd database; docker-compose up -d` | No compose file in `database/`. Run `docker compose up -d db` from `pwa-marketplace/` |
| `pnpm run dev` | No `dev` script in `frontend/package.json`. It is in each app's own package.json: `pnpm --filter customer dev` |
| `pnpm run storybook` "from shared-lib" | Script is in `frontend/package.json`, not shared-lib |
| `pnpm install` from `frontend/` | Works, but `pnpm-workspace.yaml` lists nonexistent `admin` and omits `org-admin` and `platform-admin` |
| `python -m unittest discover -s pwa-marketplace/backend/tests ...` | Only works from the git root. The single test file covers a model-conversion script, not routes/auth/search/workflows |
| `python -m scripts.generate_er_diagram` | Must run from `backend/`. Likely ImportError: it imports `models_sql2orm_flask_sqlalchemy`, which is not in `app/shared/` (unverified at runtime) |
| Tree shows `docker-compose.yml` next to CLAUDE.md, no `workflows/`, `scripts/`, `.github/` | Tree omits `backend/workflows/` (Temporal), `backend/scripts/`, `.github/` |
| Primitives list (Dropdown, ToggleSwitch) | Files exist but are not exported from `shared-lib/src/index.js`. `Label` and `FormMessage` exist and are not listed. `FormField/FormItem/FormControl`, `Alert*` also exist |
| Tokens `bg-primary/secondary/muted/card/input` | Not defined anywhere. `tailwind.config.js` colors block is commented out (Tailwind 4); `globals.css` `@theme` defines only background/text. Dark values are separate vars (`--color-background-dark`), not overrides |
| "Customer frontend at http://localhost:3000" | Correct. Others: org-admin 3001, platform-admin 3050; backends 5000/5001/5050; search 5002; Meili 7700; Temporal 7233/8233; MySQL 3306 |

Also wrong/stale in other files: root `README.md` (non-existent `backend/app/admin/`, `npm start`, old `init.sql` path), `STYLEGUIDE.md` L182-199 (undefined tokens), `backend/docs/ER_DIAGRAM_README.md` (says Users is outdated, points to the missing models file).

## 2. Legacy files and dirs agents should ignore
- **Root:** `docker-compose copy.yml`, `docker-compose.override.yml.old`, `tmp-db-stack.yml`, `.coverage`, `coverage.xml`. Git root: `marketplace-pwa (old)/` (159 tracked files), `project_structure.txt` (2.3 MB), `.mypy_cache/`.
- **Backend app:** `shared/{auth copy,management.old,models_old,search_old,search_wsgi_old}.py`, `shared/models_*` variants (live is only `models.py`), `customer/customer_management copy.py`, `org_admin/org_admin_management.old.py`.
- **Caution:** the generator scripts and `scripts/index_products_services_stores_categories.py` still import the legacy `models_sql2orm_flask_sqlalchemy.py`, so "legacy" does not mean unreferenced.
- **Workflows:** live set is `__init__`, `order_workflow`, `item_workflow`, `order_activities`, `item_activities`, `worker_runner`. All `*_old*`, `*_old2/3`, `* copy*` siblings are dead. The live `__init__.py` is itself broken (imports `process_item_shipment`; real name is `perform_item_shipment`).
- **Backend misc:** `Dockerfile copy`, `scripts/index_products_services copy.py`, `docs/ER_DIAGRAM_README copy.md`, stale `docs/er_diagram_20251101_*` outputs.
- **Database:** `init copy.sql` (dangerous, see section 4), `*.sql.bak`.
- **Frontend:** `.storybook/main.js.old`, `customer/vite.config.old.js`, `customer/src/{entry-client,entry-server,main}.old.jsx`, `org-admin/.../AdminOrderManagement.jsx.old`, `shared-lib/.../SearchBar copy*.jsx`, `frontend/admin (old)/`, Storybook `*-Storybook-Example.*` boilerplate. `frontend/*/README.md` are Vite boilerplate (customer README has some real notes).

## 3. How data is scoped and roles are enforced (as coded)
**Scoping model (from `models.py`):** Organisation owns Stores (`stores.store_organisation_id`, NOT NULL). `OrgUsers.org_user_organisation_id` is NOT NULL. Products/services are global rows; stores list them via `stores_products_services`. Orders have only `customer_id`; org/store ownership is derived through order line -> store product -> store -> organisation. `StoresUsers` exists but no code consults it.

**Backend enforcement, intended design:** JWT carries only `{user_id, exp}`. `token_required(org_id, role_codes_required)` in `shared/auth.py` loads the user and checks `role_code`. The app type is guessed from substrings (`backend-org-admin` etc.) in `request.path`.

**What actually happens (static reading, not run):**
- `auth.py:5` imports `shared/management.py`, which does not exist (only `management.old.py`). Importing auth fails, so every blueprint fails to load.
- Routes call `@token_required('org_admin', roles=[...])`, but the decorator has no `roles` kwarg (TypeError). Customer routes use bare `@token_required` (wrong usage).
- Path-substring app detection matches compose hostnames, which never appear in request paths.
- Roles read from `user.role.role_code`; the new models use `org_role` / `platform_role`. Token types are not distinguished: a customer token with id 5 validates as OrgUser 5 if routed there. Scope-from-table (CLAUDE.md) is not enforced in code.
- Only `admin`, `supervisor`, `staff` appear in routes. `viewer` is excluded by omission, not by a read-only rule. No org/platform login endpoint exists, so those tokens cannot be issued.
- **Customer** order routes filter by `customer_id` from the token (not IDOR-prone). **Org-admin** functions have no org or store filter at all (users, stores, product-services, ship/refund order), and `POST /users` takes `organisation_id` and `role_code` from the body. This is cross-tenant privilege escalation if the decorator is ever fixed.
- Platform admin sees everything by design, but `GET /organisations` has no auth, and `platform_admin_routes.py` shadows Flask `request` and imports via `backend.app...`.

## 4. init.sql vs models.py vs Alembic
- `init.sql` and the single Alembic migration (`7ec7b65c7a98`) describe the **old** schema: `users`, `store_user_role`, `cities`, `customer_addresses`, `order_details`. `models.py` is the **new** one: adds `organisations`, `org_users`, `platform_users`, `featured_stores`, `stores_users`, `cities_towns`, `customers_addresses`, `orders_details`, `store_type/city/org` on stores, Temporal ids on orders, `*_display` columns. A fresh compose DB cannot serve the live ORM.
- No ON DELETE rules anywhere. Prices are `DECIMAL(10,2)` in SQL but bare `db.Numeric` in models (MySQL treats it as `DECIMAL(10,0)`, so cents are lost if the ORM creates the table). Default 0 on filled quantity/price dropped in models.
- No seed data: `roles`, `entity_statuses`, `order_statuses` are empty on a fresh DB, but code requires `status_code='active'` and role codes `admin/supervisor/staff`.
- No triggers/history for `org_users`, `platform_users`, `organisations`, `featured_stores` (history models exist).
- `alembic.ini` defaults to `sqlite:///:memory:`; `env.py` swallows model import failure (autogenerate then silently empty). Nothing in Docker runs migrations; INIT does not stamp `alembic_version`.
- Compose mounts the whole `docker-entrypoint-initdb.d/` directory, so `init copy.sql` runs too, before `init.sql`. Triggers are identical and not `IF NOT EXISTS`, so init likely aborts on duplicate triggers (inferred from MySQL behaviour, not run).
- Ownership of `database/init.sql` path in CLAUDE.md L78/L97 is wrong.

## 5. Security and validation gaps seen in code
**High:** cross-org IDOR/escalation in org-admin functions (above); user creation stores plaintext password (`org_admin_management.py:56`) with wrong attribute names; `SECRET_KEY` falls back to literal `'dev-secret'` (`config.py:15`); audit identity (`@audit_user`) taken from an unauthenticated, non-HttpOnly `user_email` cookie (`database.py:28-34`); unauthenticated `/roles`, platform `/organisations`; no rate limiting on login/register/decode.
**Medium:** JWT 7-day HS256, no `iat/aud/jti`, no revocation; no CSRF on cookie auth (Secure cookie also breaks plain-HTTP dev); login enumerates accounts (distinct errors); `str(e)` returned to clients (`customer_management.py:255,278,449`); `except IntegrityError` imports `sqlite3.IntegrityError`; `bleach.clean` applied to passwords; `request.get_json()` unguarded (500 on empty body); client-supplied prices/stock/pic paths; no pagination (`.all()`); no stock check on orders.
**Low/ops:** entrypoint.sh:35 sets password to the secret *file path* when file is missing; compose references missing secret files (`secret_key.txt`, `meilisearch_api_key.txt`, `google_search_api_key.txt`); compose port/bind mismatches for org-admin and platform-admin (5001/5050 vs `:5000` mapping); frontend `api.js` default customer URL points to port 5001; frontend has no route guards (only cosmetic `isLoggedIn`), and `isAdmin/isSupervisor` are never true under compose (`APP_TYPE === "admin"` vs `org-admin`/`platform-admin`).
**Not found:** SQL injection (ORM and bound `text()` only), debug mode, upload handling.
**Frontend runtime bugs:** `customer/src/Routes.jsx` uses `ProductServiceList` and `CategoryProductServiceStoresPage` without importing them (may not be the live entry under SSR; unverified).
**Uncommitted work:** `backend/app/shared/auth.py` deletes the dead `Users` import (correct, but `.management` import still breaks); `Routes.jsx` is a one-word comment edit.
**Tracked `.env` files** contain only commented-out URLs, no secrets.

## 6. Proposed corrected AGENTS.md (to write after approval)
Short, operational, no duplication of CLAUDE.md, and it does **not** import CLAUDE.md or itself. Draft content:

```markdown
# AGENTS.md — Operating rules for AI agents

Project context lives in CLAUDE.md. This file covers how agents work here.
Paths are relative to `pwa-marketplace/`.

## Team structure
- **Backend agent** — `backend/app/**`, `backend/workflows/**`. Owns Flask routes, models, auth, Temporal.
- **Frontend agent** — `frontend/**`. Must read STYLEGUIDE.md first; use `shared-lib` primitives.
- **Database agent** — `database/docker-entrypoint-initdb.d/init.sql`, `backend/alembic/**`. Keeps init.sql, models.py and migrations consistent.
- **Reviewer** — read-only; checks the Security checklist before any merge.
Agents stay in their lane; cross-lane changes are proposed to the owner, not made.

## Access policy
- Read/write only within the lane above. Never edit: `database/secrets/**`, `.env*`, `docker-compose*.yml`, `*.lock`, generated `backend/docs/er_diagram_*`.
- Never commit, push, or run `docker compose down -v` / destructive DB commands without explicit user approval.
- Never print secrets or user data; refer to variable names only.

## Ignore (legacy — do not read, edit or import)
`*.old.*`, `*_old*`, `*copy*`, `*.bak`, `backend/app/shared/models_*.py` (live: `models.py`), `backend/workflows/*_old*` and `* copy*` (live: `order_workflow`, `item_workflow`, `order_activities`, `item_activities`, `worker_runner`), `database/docker-entrypoint-initdb.d/init copy.sql` and `*.bak`, `frontend/admin (old)`, repo-root `marketplace-pwa (old)/`, `project_structure.txt`, `.coverage`, `coverage.xml`.
Exception: generator scripts under `backend/scripts/` still reference legacy models — don't "clean up" without checking.

## Data scoping & roles
- Scope comes from the table: `OrgUsers` (always tied to one organisation), `PlatformUsers` (all organisations), `Customers` (no roles).
- Organisation owns Stores (`stores.store_organisation_id`). Products/services are global; stores list them via `stores_products_services`. Orders carry only `customer_id`; derive org/store via order line -> store.
- Every org-admin query must filter by the **caller's** organisation taken from the authenticated user, never from the request body or URL. Verify store/order ownership before mutating.
- Branch on user table before interpreting a role. Viewer must be rejected on every write.

## Security checklist (before finishing any backend/DB task)
1. Org/store ownership checked server-side on every read and write.
2. Role check present; token type matches the app (customer vs org vs platform).
3. Passwords hashed (`generate_password_hash`); never stored or logged in plain text.
4. No hard-coded secrets or fallback keys; secrets come from env/files.
5. Input validated (types, ranges, required keys); no mass assignment of `organisation_id`, `role_*`, `*_status_id`.
6. Errors don't leak `str(e)`; list endpoints are paginated.
7. Schema change touches `init.sql`, `models.py` and an Alembic migration together.

## Known issues (don't assume these work)
auth imports missing `shared/management.py`; `platform_admin` has no `create_app`/`wsgi.py`; init.sql/Alembic describe the old schema; lookup tables are unseeded; `workflows/__init__.py` import is broken; compose secret files and some port mappings are missing/wrong.

## Commands (verified paths)
- DB: `docker compose up -d db` (from `pwa-marketplace/`; init runs only on an empty volume)
- Full stack: `docker compose up` (customer :3000, org-admin :3001, platform-admin :3050)
- Frontend (from `frontend/`): `pnpm install`; `pnpm --filter customer dev`; `pnpm run storybook`
- Backend tests (from git root): `python -m unittest discover -s pwa-marketplace/backend/tests -p "*_test.py" -v` (covers only the model-conversion script)
- ER diagram (from `backend/`): `python -m scripts.generate_er_diagram` (currently likely broken)
- Search engine build: `docker build -f backend/Dockerfile-search --build-arg SEARCH_ENGINE=meili ...`

## End-of-task report
1. What changed (files, 1 line each) 2. Lane/ownership respected? 3. Checklist items verified / not verified 4. Tests run and result (or "not run") 5. Follow-ups or risks.
```

## 7. Proposed CLAUDE.md changes (separate; apply only if you approve)
1. L78, L97: `database/init.sql` -> `database/docker-entrypoint-initdb.d/init.sql`.
2. L227: `SEARCH_ENGINE_SWITCH.md` -> `backend/SEARCH_ENGINE_SWITCH.md`; fix the build-arg example to `-f Dockerfile-search`.
3. L137: replace "no global `create_app()`" with "`app/__init__.py` has a stub only; `platform_admin` has none yet".
4. Developer Workflows block: correct cwd for tests and ER diagram; replace `pnpm run dev` and "storybook from shared-lib"; replace `cd database; docker-compose up -d` with `docker compose up -d db`.
5. Design tokens: note `bg-primary/secondary/muted/card/input` are not currently defined; dark tokens are separate variables.
6. Add the `@AGENTS.md` import (one direction only) and a pointer to the Ignore list.
7. Add the missing `## Changelog` section the Self-Maintenance Rule refers to.
8. Optional: the "Current Development Status" section should list the known schema drift (init.sql/Alembic stale vs models.py).
Related STYLEGUIDE.md and README.md fixes are out of scope here; flag only.

## Verification once approved
- Re-read the written AGENTS.md; check every path with `ls`/`git ls-files`; confirm no `@` import cycle.
- Confirm CLAUDE.md still loads (only if its edits are approved).
- `git status` shows only the intended files (AGENTS.md, optionally CLAUDE.md); nothing committed.