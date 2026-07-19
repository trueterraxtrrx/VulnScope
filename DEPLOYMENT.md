# VulnScope V1.5 Deployment Notes

This public version is prepared for local/demo hosting, not production operation.

## Build

```bash
cd frontend
pnpm install
pnpm run build
```

## Backend

```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Docker

```bash
cp .env.example .env
docker compose up --build
```

## Demo Hosting

- Set `DEMO_MODE=true` and `VITE_DEMO_MODE=true`.
- Set `CORS_ORIGINS` to the hosted frontend origin.
- Run migrations before starting the API.
- Do not publish real vulnerability inventories or private imports.
<!-- Project version: VulnScope V1.5 -->







