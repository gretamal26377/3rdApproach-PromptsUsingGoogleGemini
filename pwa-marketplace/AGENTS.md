# AGENTS.md — Team Structure for pwa-marketplace

Defines how AI agents are organised when working on this repo. Three teams, one per audience. Each team owns a frontend and a backend that must stay aligned.

**Source of truth (settled unless the user explicitly revisits):**
- `CLAUDE.md` — architecture, schema, naming conventions, workflows
- `STYLEGUIDE.md` — all UI/UX rules, design tokens, shared-lib components

If this file conflicts with either, they win. Flag the conflict instead of choosing silently.

---

## Teams

| Team | Audience | Frontend | Backend |
|---|---|---|---|
| **Customer** | Shoppers | `frontend/customer` (PWA + SSR) | `backend/app/customer` |
| **Org Admin** | Organisation staff (Admin, Supervisor, Staff, Viewer) | `frontend/org-admin` (CSR) | `backend/app/org_admin` |
| **Platform Admin** | Platform operators | `frontend/platform-admin` (CSR) | `backend/app/platform_admin` |

Shared code (used by all teams): `frontend/shared-lib`, `backend/app/shared` (models, DB, auth, search, utils).

### Team scope

- **Customer** — search/browse, stores, cart, checkout, order history. Owns PWA and SSR concerns.
- **Org Admin** — stores, products/services, prices, categories, organisation users and roles.
- **Platform Admin** — cross-organisation oversight of organisations, stores, users, orders.

### Inside each team

Every team works as a frontend + backend pair:
- **Backend member** — Flask routes and business logic in the team's app; uses shared models/auth.
- **Frontend member** — React app; uses `shared-lib` primitives and follows `STYLEGUIDE.md`.
- **Alignment rule** — the API contract (route, method, payload, error shape) is defined first by the backend member, then consumed by the frontend member. Never change one side of a contract without updating the other in the same task.

---

## Access policy

- **Full cross-team access:** any team may read and write any part of the repo, including other teams' apps and shared code.
- **The user is the sole reviewer.** Changes are applied to the working tree, uncommitted, on a feature branch. The user accepts or rejects them afterwards.
- Never commit, push, merge, force-push, or delete branches without explicit approval.
- Do not delete `*.old.*`, `*_copy*`, or `models_*.py` variants. They are intentional artifacts; ask first.

### Cross-boundary reporting (mandatory)

Because access is unrestricted, the review depends on visibility. At the end of every task, list under **Cross-boundary changes**:
- Files edited outside the acting team's own app
- Any change in `frontend/shared-lib` or `backend/app/shared`
- Any change to auth, models/schema, Alembic migrations, `database/init.sql`, search, or Temporal order workflows
- For each: what changed, why, and which other apps it can affect

Shared-code changes should be backward-compatible by default. If a breaking change is unavoidable, say so explicitly and update every affected app in the same task.

---

## Workflow per task

1. **Plan first** for anything touching more than one file or app: state the approach, affected teams, and cross-boundary files. Wait for approval on non-trivial plans.
2. **Backend before frontend** when a contract changes.
3. **Schema changes:** keep `models.py`, the Alembic migration, and `database/init.sql` consistent.
4. **Tests:** add or update tests for changed behaviour; run them and report results honestly, including failures.
5. **Summarise** using the report format below.

---

## Security and validation checklist

Check every change against this list. **Proactively flag gaps even when not asked.**

- **Server-side validation:** never rely on frontend (Zod/React Hook Form) validation. Validate and sanitise all input in Flask.
- **Authentication:** every non-public route requires auth. Flag any route missing it.
- **Authorisation by role:** enforce Admin/Supervisor/Staff/Viewer permissions on the backend. Viewer must be read-only server-side, not just hidden in the UI.
- **Tenant isolation:** Org Admin queries must be scoped to the user's own organisation. Check every lookup by ID for cross-organisation access (IDOR).
- **Customer data isolation:** customers can only access their own cart, orders, and profile.
- **Platform Admin routes:** restricted to platform admins only; verify nothing is reachable from the other two apps.
- **Database access:** use SQLAlchemy parameterised queries; no string-built SQL.
- **Secrets:** never hard-code credentials or keys; use environment variables.
- **Errors and logs:** no stack traces or sensitive data in responses or logs.
- **Pricing and order integrity:** compute totals and prices server-side; never trust client-submitted amounts.

---

## Frontend rules (summary)

Full detail lives in `STYLEGUIDE.md`.
- Use `shared-lib` primitives before creating new components; update `STYLEGUIDE.md` if a new primitive is added.
- Tailwind only, using the design tokens.
- Forms never reset on validation failure; call `form.reset()` only after a successful create/update.
- Dropdowns and checkboxes: use the `shared-lib` versions (animation, keyboard navigation, ARIA).

---

## End-of-task report format

```
## Summary
What was done and why.

## Files changed
Grouped by team (Customer / Org Admin / Platform Admin / Shared).

## Cross-boundary changes
Per the policy above, or "None".

## Security / validation notes
Gaps found, fixed, or left open.

## Tests
What was run and the result.
```

---

## Keeping docs current

After significant structural changes (new module, schema change, new pattern), **propose** updates to `CLAUDE.md` and this file in the summary. Do not edit either file without the user's approval.