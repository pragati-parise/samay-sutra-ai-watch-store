# Samay Sutra | AI-Powered Watch E-Commerce Platform

Samay Sutra is a full-stack watch e-commerce platform built with a separate React frontend and FastAPI backend. Customers can browse watches, search and filter the catalogue, create an account, manage a cart, place orders, view order history, and ask an AI shopping assistant for catalogue-grounded suggestions.

## Tech stack

- Frontend: React, Vite, HTML, CSS, JavaScript
- Backend: Python, FastAPI, REST APIs
- Database: PostgreSQL (Neon), SQLAlchemy ORM
- Authentication: JWT, Passlib, and bcrypt password hashing
- AI: Google Gemini API
- Deployment: Render Static Site + Render Web Service

## Architecture

```text
React + Vite frontend (port 5173)
             |
             | REST API requests
             v
FastAPI backend (port 8000) ----> Gemini API
             |
             v
       Neon PostgreSQL
```

The frontend and backend run separately. The React app uses `VITE_API_BASE_URL` to call FastAPI. FastAPI manages database access, JWT authentication, product images, orders, and all Gemini API calls. The Gemini key is never exposed in the frontend.

## Features

- Product catalogue, search, category and brand filters, price sorting
- Product image gallery-style cards and responsive premium watch-store UI
- User registration and login with bcrypt-hashed passwords and JWT tokens
- Protected persistent cart: add, update quantity, remove
- Checkout, order placement, and My Orders history
- Product reviews API and wishlist API
- AI watch recommendations using actual available database products
- AI shopping assistant with concise product recommendations
- Admin-only Gemini product-description draft endpoint; generated text is editable before saving
- Mobile, tablet, and desktop responsive layout

## Project structure

```text
.
├── backend/
│   ├── routers/          # Store and AI REST routes
│   ├── services/         # Gemini service
│   ├── auth.py           # JWT and password hashing
│   ├── database.py       # SQLAlchemy connection
│   ├── models.py         # PostgreSQL models
│   └── main.py           # FastAPI application
├── frontend/
│   ├── src/main.js       # React UI
│   ├── src/style.css     # Store styling
│   ├── .env.example      # Frontend API URL template
│   └── package.json
├── static/images/        # Product images served by FastAPI
├── scripts/migrate_sqlite.py
├── .env.example          # Backend environment template
├── requirements.txt
└── render.yaml
```
