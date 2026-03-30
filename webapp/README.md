# yojenkins Web Application

React + TypeScript frontend for yojenkins, built with Vite.

## Architecture

```
Browser  <-->  React SPA (webapp/)  <-->  FastAPI (yojenkins/api/)  <-->  YoJenkins business logic
```

The web layer is a thin wrapper around the same `YoJenkins` class used by the CLI.
Each authenticated user gets their own `YoJenkins` instance in a server-side session.

## Development

```bash
# Terminal 1: API server with auto-reload
pip install -e ".[web]"
yojenkins serve --reload --no-frontend

# Terminal 2: Vite dev server with hot reload (proxied to API)
cd webapp
npm install
npm run dev
```

Vite runs on port 5173, API on 8090. CORS is pre-configured for both.

## Production

```bash
yojenkins serve          # auto-builds frontend if needed
yojenkins serve --build  # force rebuild
```

Built files in `webapp/dist/` are served by FastAPI as a single-page application.

## Project Structure

- `src/pages/` — Page components (login, dashboard, job detail, etc.)
- `src/components/` — Reusable UI components
- `src/api/` — API client and React Query hooks
