# Samay Sutra — AI-Powered Watch E-Commerce Platform

Samay Sutra is a full-stack watch store with a **separate React/Vite frontend** and **FastAPI REST backend**. The API uses PostgreSQL through SQLAlchemy, JWT authentication, and Gemini for catalogue-grounded shopping help.

## Architecture

```text
React + Vite (localhost:5173) → FastAPI REST API (localhost:8000) → Neon PostgreSQL
                                      └→ Gemini API
```

The frontend is in `frontend/`; it calls the backend through `VITE_API_BASE_URL`. FastAPI serves APIs and product images only. This separation makes it easy to study and deploy the client and server independently.

## Main features

- Product browsing, search, category/brand filters, cart, checkout, orders, wishlist and reviews
- JWT login/register with bcrypt password hashes
- PostgreSQL tables for users, products, categories, carts, orders, wishlist and reviews
- Gemini recommendation and shopping-assistant APIs limited to actual catalogue data
- Admin-only editable Gemini product-description drafts

## Local setup

### 1. Backend

Use Python 3.11. Create `.env` at repository root from `.env.example`, add the Neon/PostgreSQL URL, a JWT secret, and Gemini key. Then run:

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

Backend docs: `http://127.0.0.1:8000/docs`

### 2. Frontend

Open a second terminal:

```powershell
cd frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Frontend: `http://localhost:5173`

For local development, `frontend/.env` should contain:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Database migration

To move legacy data from `watch_store.db` into an empty PostgreSQL database, configure the root `.env` first, then run:

```powershell
python scripts/migrate_sqlite.py
```

It imports existing products, users, orders and order items.

## Deployment

Deploy two Render services: a Python Web Service from the repository root and a Static Site built from `frontend/`. Set backend `DATABASE_URL` to the Neon connection string and `FRONTEND_ORIGINS` to the final frontend Render URL. Set frontend `VITE_API_BASE_URL` to the final backend Render URL. The included `render.yaml` is a Blueprint starting point.

## API overview

- Auth: `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`
- Catalogue: `GET /api/products`, `GET /api/products/{id}`, `GET /api/categories`
- Shopping: `/api/cart`, `/api/wishlist/{id}`, `/api/orders`
- AI: `POST /api/ai/assistant`, `/api/ai/recommendations`, `/api/ai/product-description`

Protected requests use `Authorization: Bearer <JWT>`.
