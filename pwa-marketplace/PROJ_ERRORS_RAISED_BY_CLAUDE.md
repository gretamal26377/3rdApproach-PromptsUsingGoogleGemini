# Plan: audit the corrected AGENTS.md and propose fixes

## Context
You replaced the draft `AGENTS.md` (now 116 lines: three feature teams, access policy, security checklist, report format). The old draft was a CLAUDE.md copy, so the old comparison no longer applies. I re-read AGENTS.md, CLAUDE.md and STYLEGUIDE.md and re-checked the claims against the repo. Backend, schema and security findings still hold: the code has not changed since the earlier audits (only AGENTS.md is modified; commit 348 only touched `auth.py`, `Routes.jsx` and two docs). Items marked (unverified) were read from code, not run. Nothing has been edited.

The new draft is much better. Keep its structure (Teams table, Access policy, Cross-boundary reporting, checklist, report format). The fixes below are targeted.

## Files that would be modified once approved
- `pwa-marketplace/AGENTS.md` — targeted corrections (section 6). Always.
- `pwa-marketplace/CLAUDE.md` — only the fixes in section 7, and only if you approve them.
- Nothing else. All code, schema and config bugs below are reported, not fixed. No commit, no push.
- Flag only: `PROJ_ERRORS_RAISED_BY_CLAUDE.md` (committed in 348) is a copy of my earlier plan. Its "proposed AGENTS.md" is for the rejected draft, so it is now misleading. Suggest deleting or replacing it; I won't touch it unless you say so.

## 1. Paths and claims in the draft that are wrong
| Draft says | Reality |
|---|---|
| `database/init.sql` (L50, L61) | `database/docker-entrypoint-initdb.d/init.sql` (CLAUDE.md L78/L97 has the same error) |
| "Do not delete `*.old.*`, `*_copy*`, `models_*.py`" (L43) | `*_copy*` matches **0** files. Real names are `* copy.*` with a space (14 tracked), `_old`, `_old2/3`, `.old`, `.jsx.old`, `.bak`, `(old)` dirs (20). `*.old.*` matches only 6. Patterns need rewriting |
| "Changes... on a feature branch" (L41) | No feature branches exist. Work happens on `develop` (also `develop2`, `development`, `test`, `main`). State which branch agents use |
| "CLAUDE.md — architecture, schema, naming conventions, workflows" (L6) | CLAUDE.md has no naming conventions, and its schema entry points to the wrong path |
| "Customers can only access their own cart" (L75) | No server-side cart. The cart is `localStorage` in the customer app. Customer isolation really covers orders, profile and addresses |
| "Keep `models.py`, Alembic and `database/init.sql` consistent" (L61) | They are already inconsistent (section 4). The draft names no source of truth |
| "Do not edit CLAUDE.md or this file without approval" (L117) vs CLAUDE.md Self-Maintenance Rule | Direct conflict: CLAUDE.md says to append to a `## Changelog` after structural changes, and that section does not exist. L9 says CLAUDE.md wins, so the draft needs an explicit exception or CLAUDE.md needs changing |
| "Add or update tests... run them" (L62) | One test file exists, for a model-conversion script. No tests for routes, auth, search or workflows. The command only works from the git root |
| "Use shared-lib dropdowns/checkboxes" (L90) | `Dropdown` and `ToggleSwitch` exist but are not exported from `shared-lib/src/index.js` |
| Viewer "read-only server-side" (L73) | No `viewer` role appears in any route and the roles table is not seeded |

Correct as written: the three team rows (`frontend/customer`, `org-admin`, `platform-admin`; `backend/app/customer`, `org_admin`, `platform_admin`) and shared paths `frontend/shared-lib`, `backend/app/shared` all exist. Server-side pricing (L80): `create_order_logic` computes totals from `sps.price` in the DB — good.

Team-table caveats: `backend/app/platform_admin` has no `create_app` or `wsgi.py`, so that app cannot start. `org-admin` and `platform-admin` are missing from `frontend/pnpm-workspace.yaml` (which lists a nonexistent `admin`).

Missing from the draft: ignore list, known issues, verified commands, the table-vs-role rule from CLAUDE.md, org -> store -> order derivation, owner for `backend/workflows` and search.

## 2. Legacy files and dirs agents should ignore
- **Root:** `docker-compose copy.yml`, `docker-compose.override.yml.old`, `tmp-db-stack.yml`, `.coverage`, `coverage.xml`. Git root: `marketplace-pwa (old)/` (159 tracked files), `project_structure.txt` (2.3 MB), `.mypy_cache/`.
- **Backend app:** `shared/{auth copy,management.old,models_old,search_old,search_wsgi_old}.py`, `shared/models_*` variants (live: `models.py` only), `customer/customer_management copy.py`, `org_admin/org_admin_management.old.py`.
- **Caution:** the generator scripts and `scripts/index_products_services_stores_categories.py` still import `models_sql2orm_flask_sqlalchemy.py`. Legacy does not always mean unreferenced.
- **Workflows:** live set is `__init__`, `order_workflow`, `item_workflow`, `order_activities`, `item_activities`, `worker_runner`. All `*_old*`, `*_old2/3`, `* copy*` siblings are dead. The live `__init__.py` itself imports a function that doesn't exist.
- **Backend misc:** `Dockerfile copy`, `scripts/index_products_services copy.py`, `docs/ER_DIAGRAM_README copy.md`, `docs/er_diagram_20251101_*`.
- **Database:** `init copy.sql` (dangerous: compose mounts the whole directory, so it runs; see section 4), `*.sql.bak`.
- **Frontend:** `.storybook/main.js.old`, `customer/vite.config.old.js`, `customer/src/{entry-client,entry-server,main}.old.jsx`, `AdminOrderManagement.jsx.old`, `SearchBar copy*.jsx`, `frontend/admin (old)/`, Storybook `*-Storybook-Example.*`.
- **Outdated docs:** root `README.md` (nonexistent `backend/app/admin/`, `npm start`, old `init.sql` path), `backend/docs/ER_DIAGRAM_README.md`, `frontend/org-admin|platform-admin/README.md` (Vite boilerplate), STYLEGUIDE.md L182-199 (undefined tokens).

## 3. How data is scoped and roles are enforced
**Model (`models.py`):** Organisation owns Stores (`stores.store_organisation_id`, NOT NULL). `OrgUsers.org_user_organisation_id` is NOT NULL. Products/services are global rows; stores list them via `stores_products_services`. Orders carry only `customer_id`; org/store ownership is derived order line -> store product -> store -> organisation. `StoresUsers` exists but no code uses it. So scoping is by **organisation**, not by store.

**Intended enforcement (`shared/auth.py`):** JWT holds `{user_id, exp}`. `token_required(org_id, role_codes_required)` loads the user and checks `role_code`. App type is guessed from substrings like `backend-org-admin` in `request.path`.

**Actual (static reading):**
- `auth.py:5` imports `shared/management.py`, which does not exist (only `management.old.py`), so every blueprint fails to import.
- Org/platform routes call `@token_required('org_admin', roles=[...])`; the decorator has no `roles` kwarg. Customer routes use bare `@token_required`.
- Path-substring app detection matches compose hostnames, which never appear in request paths.
- Roles are read from `user.role.role_code`; the new models use `org_role` / `platform_role`.
- Token types are not distinguished (customer id 5 would validate as OrgUser 5). CLAUDE.md's "scope comes from the table" is not enforced.
- No login endpoint exists for org or platform users.
- Only `admin`, `supervisor`, `staff` appear in routes; `viewer` is excluded by omission only.
- Customer order routes correctly filter by token `customer_id`. Org-admin functions have no org or store filter, and `POST /users` takes `organisation_id` and `role_code` from the body.
- Platform admin: `GET /organisations` has no auth; `platform_admin_routes.py` shadows Flask `request` and imports via `backend.app...`.

## 4. init.sql vs models.py vs Alembic
- `init.sql` and the single migration `7ec7b65c7a98` describe the **old** schema (`users`, `store_user_role`, `cities`, `customer_addresses`, `order_details`). `models.py` is the **new** one (`organisations`, `org_users`, `platform_users`, `featured_stores`, `stores_users`, `cities_towns`, `customers_addresses`, `orders_details`, store type/city/org, Temporal ids on orders, `*_display` columns). A fresh compose DB cannot serve the live ORM.
- Prices are `DECIMAL(10,2)` in SQL but bare `db.Numeric` in models (MySQL: `DECIMAL(10,0)`, cents lost if the ORM creates the table). No ON DELETE rules anywhere.
- No seed data: `roles`, `entity_statuses`, `order_statuses` are empty on a fresh DB, but code needs `status_code='active'` and roles `admin/supervisor/staff`.
- No history triggers for `org_users`, `platform_users`, `organisations`, `featured_stores`.
- `alembic.ini` defaults to `sqlite:///:memory:`; `env.py` swallows model import failures, so autogenerate can silently diff nothing. Nothing in Docker runs migrations, and init does not stamp `alembic_version`.
- Compose mounts the whole `docker-entrypoint-initdb.d/` directory, so `init copy.sql` runs before `init.sql`. Their triggers are identical (the files differ only in comments, checked) and not `IF NOT EXISTS`, so init likely aborts (inferred from MySQL behaviour, not run).

## 5. Security and validation gaps, mapped to the draft's checklist
| Checklist item (L71-80) | Status in code |
|---|---|
| Server-side validation | Weak: unguarded `request.get_json()`, no type/range checks (quantity, price, stock), client-supplied pic paths |
| Authentication on non-public routes | Fails: unauthenticated `/roles`, platform `/organisations`; the decorator is miswired so no route works as written |
| Role authorisation, Viewer read-only | Not enforced: `viewer` is absent; roles read from a field that no longer exists |
| Tenant isolation / IDOR | **Fails** in org-admin users, stores, product-services, ship/refund order, and `organisation_id`/`role_code` from the body (privilege escalation) |
| Customer data isolation | Orders OK; no server cart; `/decode` returns user details for any submitted token |
| Platform-admin separation | Relies on path substring only |
| No string-built SQL | **Pass** (ORM and bound `text()`) |
| No hard-coded secrets | **Fails**: `'dev-secret'` fallback (`config.py:15`); entrypoint sets password to the secret *file path* when the file is missing; compose references missing secret files |
| No leaked errors | **Fails**: `str(e)` returned (`customer_management.py:255,278,449`); login distinguishes unknown email from wrong password |
| Server-side prices | **Pass** for orders; org-admin accepts price from body |

Other high/medium items: plaintext password on org-user creation (`org_admin_management.py:56`) with wrong attribute names; audit identity from an unauthenticated `user_email` cookie (`database.py:28-34`); no rate limiting; JWT 7-day HS256 with no revocation; no CSRF protection on cookie auth; `except IntegrityError` imports the sqlite one; no pagination. Frontend: no route guards, `isAdmin/isSupervisor` never true under compose, `Routes.jsx` uses two components it doesn't import (unverified whether it is the live entry). Tracked `.env` files hold only commented URLs, no secrets. Not found: SQL injection, debug mode, upload handling.

## 6. Proposed corrected AGENTS.md (targeted edits to your draft)
Keep L1-35 (teams) and L84-111 unchanged. Apply:

1. **L6-9 / L43 / L50 / L61:** replace `database/init.sql` with `database/docker-entrypoint-initdb.d/init.sql`; drop "naming conventions".
2. **L41:** "...on the `develop` branch (or a branch the user names)" — state the real branch rule.
3. **L43:** replace with:
   > Do not delete legacy files (`*.old.*`, `*_old*`, `* copy*`, `*.bak`, `models_*.py` variants, `(old)` dirs). Do not read or import them either, except where listed in Known issues. Ask before removing.
4. **L75:** "Customers can only access their own orders, profile and addresses (the cart is client-side)."
5. **L61 (schema rule):** add: "Source of truth is `models.py`. Today `init.sql` and the Alembic migration lag behind it; update them together with any schema change and say so in the report."
6. **L62 (tests):** add: "Only `backend/tests/convert_models_transform_test.py` exists today; run from the git root."
7. **L117:** add the exception: "Appending to CLAUDE.md `## Changelog` per its Self-Maintenance Rule is allowed without approval; all other edits need approval."
8. **New section "Data scoping and roles"** (after Teams):
   - Scope comes from the table: `OrgUsers` (one organisation), `PlatformUsers` (all), `Customers` (no roles). Branch on the table before interpreting a role.
   - Organisation owns Stores. Products/services are global. Orders derive org/store via order line -> store product -> store.
   - Take the caller's organisation from the authenticated user, never from the body or URL.
9. **New section "Known issues (don't assume these work)":** auth imports missing `shared/management.py`; decorator misuse in all route files; `platform_admin` has no `create_app`/`wsgi.py`; `init.sql` and Alembic describe the old schema; lookup tables unseeded; `init copy.sql` also loads; `workflows/__init__.py` import broken; compose secret files missing and some port mappings wrong; generator scripts still reference legacy models.
10. **New section "Commands (verified)":** `docker compose up -d db` (from `pwa-marketplace/`); `docker compose up` (customer :3000, org-admin :3001, platform-admin :3050); from `frontend/`: `pnpm install`, `pnpm --filter customer dev`, `pnpm run storybook`; tests from git root: `python -m unittest discover -s pwa-marketplace/backend/tests -p "*_test.py" -v`; ER diagram from `backend/` (likely broken); search build `-f backend/Dockerfile-search --build-arg SEARCH_ENGINE=meili`.
11. **Teams table:** add a row or note for shared-owned areas: `backend/workflows` (Temporal), search, `database/` — "Shared; changes follow the cross-boundary report".

## 7. Proposed CLAUDE.md changes (separate; only if you approve)
1. L78, L97: `database/init.sql` -> `database/docker-entrypoint-initdb.d/init.sql`.
2. L227: `SEARCH_ENGINE_SWITCH.md` -> `backend/SEARCH_ENGINE_SWITCH.md`; build-arg example needs `-f Dockerfile-search`.
3. L137: replace "no global `create_app()`" with "`app/__init__.py` has a stub only; `platform_admin` has none yet".
4. Developer Workflows: fix cwd for tests/ER diagram; replace `pnpm run dev`, "storybook from shared-lib" and `cd database; docker-compose up -d`.
5. Design tokens: note `bg-primary/secondary/muted/card/input` are not defined; dark tokens are separate variables.
6. Add a one-way `@AGENTS.md` import. Claude Code reads CLAUDE.md, not AGENTS.md, so without it these rules don't load. AGENTS.md must not import CLAUDE.md back.
7. Add the missing `## Changelog` section.
8. Optional: list the known schema drift under "Current Development Status".
Out of scope, flag only: README.md and STYLEGUIDE.md fixes.

## Verification once approved
- Re-read AGENTS.md; check every path with `ls`/`git ls-files`; confirm legacy glob patterns match real files; confirm no `@` import cycle.
- If CLAUDE.md is edited, confirm the `@AGENTS.md` import resolves.
- `git status` shows only the intended files; nothing committed.