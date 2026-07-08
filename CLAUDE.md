# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

Two independent deployables that share one repo, with no build step or bundler:

1. **Backend API** (`server.js`, `universityModel.js`) — an Express/Mongoose REST API backed by MongoDB Atlas, deployed on Render at `https://dakhla-unity-api.onrender.com` (remote: `dakhla-unity-api-backend`). Serves university/program data to a Unity client and to the admin dashboard.
2. **Admin dashboard** (`index.html`) — a single-file vanilla JS/CSS SPA (no framework, no `<script src>` dependencies besides Google Fonts/Material Icons). It is a static file with no dev server of its own; open it directly in a browser or serve it via any static host. It talks to the **deployed** Render API by default (`API_BASE` / `API_VERIFY` constants near the top of the `<script>` block), not to a local server — update those constants if testing against a local backend.

There is no shared build pipeline between the two — editing one never requires touching the other unless the API contract changes.

## Commands

```bash
npm install        # install backend deps (express, mongoose, cors, dotenv)
node server.js      # run the API locally (reads .env for MONGO_URI, PORT, ADMIN_API_KEY)
node --check server.js   # quick syntax check (no test suite configured — package.json's "test" script is a stub)
```

There is no lint config, no test framework, and no bundler in this repo. `index.html` needs no build step — edit and reload.

### Local env requirements

`.env` (gitignored) must define `MONGO_URI` and `PORT`. `server.js` also reads `process.env.ADMIN_API_KEY` for the `verifyApiKey` middleware — set it locally if you need to exercise secured routes (`POST`/`PUT`/`DELETE` on `/api/universities`, and `GET /api/verify`).

## Backend architecture (`server.js`)

- CORS is registered **before** everything else, including an explicit `app.options(/(.*)/, cors())` for preflight — this ordering matters and was previously a source of bugs; don't reorder without reason.
- `verifyApiKey` middleware checks the `x-api-key` header against `ADMIN_API_KEY` and returns `403` on mismatch. Only mutating routes are behind it:
  - Public: `GET /api/universities`, `GET /api/unity-export` (identical data, different response shape — `unity-export` wraps in `{ universities: [...] }` for the Unity client, `/api/universities` returns a bare array for the dashboard).
  - Secured: `GET /api/verify` (used by the dashboard login screen to validate a key before storing it in `localStorage`), `POST /api/universities`, `PUT /api/universities/:id`, `DELETE /api/universities/:id`.
- `PUT`/`DELETE` on `/api/universities/:id` return `404` when no document matches — don't regress this to silently returning `200`/`null`.
- Data model (`universityModel.js`): a `University` document embeds an array of `Program` subdocuments (`programs: [ProgramSchema]`). There is no separate Programs collection — program CRUD happens by rewriting the parent university's whole `programs` array via `PUT /api/universities/:id`. Universities are looked up by their own `id` string field (not Mongo `_id`) throughout the API and frontend.

## Frontend architecture (`index.html`)

Single file, single global `<script>` block, no modules. Key patterns to preserve when extending it:

- **State**: `allUniversities` (raw array from the API) is filtered/sorted client-side in `applyFilters()`/`renderGrid()`; no server-side query params exist for search/sort/filter.
- **Auth**: the admin API key is stored in `localStorage` (`dakhla_api_key`), sent as `x-api-key` on every request, and validated once at login via `GET /api/verify`. There's no session/token expiry — a stored key is trusted until a request comes back `403`.
- **Program editing**: `openProgramsModal()` deep-clones the target university into `currentUniForPrograms` and all add/edit/remove operations happen on that local copy. Nothing is persisted until `commitProgramsToBackend()` `PUT`s the whole object — closing the modal without saving discards local changes.
- **HTML injection**: all user-controlled strings rendered into template literals go through `escapeHtml()` (escapes `& < > " '`). Any new field displayed in `renderGrid()`/`renderProgramsList()` must be escaped the same way, including values interpolated inside inline `onclick='...'` attribute strings (single-quoted attributes — the `'` escaping specifically matters here).
- **Modals**: `openModal`/`closeModal` toggle `.active` plus a CSS transition-driven `display` swap; `confirmDialog` is a special case using a Promise (`showConfirm`/`_confirmResolve`) instead of a callback — any new dismissal path (Escape, overlay click, new buttons) must resolve that promise via `dismissConfirm()`, not just hide the modal, or the awaiting caller hangs.
- `sendRequest()` is the single fetch wrapper for all mutating calls; it centralizes `403`→"access denied" and `404`→"no longer exists, refetch" toast handling. Route new mutating calls through it rather than calling `fetch` directly.

## Other files

- `clean_universities.json` — a standalone 210-entry data export/seed matching the `University` schema shape. Not read by any code in this repo (not imported by `server.js` or `index.html`); treat it as a reference/import source for manually seeding MongoDB, not a live dependency.
- `Dakhla_Data/` — contains only `.venv`/`.idea`, no tracked files; unrelated to the Node app.
