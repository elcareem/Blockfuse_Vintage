# Blockfuse Vintage — Backend API

Production-ready e-commerce REST API for **Blockfuse Vintage**, a vintage shirt brand.
Built with **FastAPI**, **MySQL 8**, **SQLAlchemy**, **Alembic**, **Cloudinary**, and deployed via **Docker + Gunicorn**.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI (Python 3.11) |
| Database | MySQL 8 |
| ORM | SQLAlchemy 2 |
| Migrations | Alembic |
| Authentication | JWT (python-jose) + bcrypt (passlib) |
| Image Upload | Cloudinary SDK |
| Production Server | Gunicorn + Uvicorn Workers |
| Containerisation | Docker (multi-stage) + docker-compose |
| DB Admin UI | phpMyAdmin |

---

## Project Structure

```
vintique/
├── app/
│   ├── main.py            # FastAPI entry point, CORS, routers
│   ├── config.py          # Pydantic Settings (.env reader)
│   ├── database.py        # SQLAlchemy engine + session
│   ├── models/            # ORM models (User, Product, Cart, Order…)
│   ├── schemas/           # Pydantic request/response schemas
│   ├── routes/            # Route handlers (auth, products, cart, orders, admin, inventory)
│   ├── services/          # Business logic layer
│   ├── core/              # JWT security + FastAPI dependencies
│   └── utils/             # Logger + HTTP exception helpers
├── alembic/               # Database migrations
├── alembic.ini
├── requirements.txt
├── gunicorn.conf.py       # Production Gunicorn config
├── Dockerfile             # Multi-stage build
├── docker-compose.yml     # App + MySQL + phpMyAdmin
└── .env.example           # Environment variable template
```

---

## Quick Start (Docker)

### 1. Clone and configure
```bash
git clone <repo-url>
cd vintique
cp .env.example .env
# Edit .env — fill in JWT_SECRET_KEY and Cloudinary credentials
```

### 2. Build and start services
```bash
docker compose up --build -d
```

### 3. Run database migrations
```bash
docker compose exec app alembic upgrade head
```

### 4. Access services
| Service | URL |
|---|---|
| API | http://localhost:8000 |
| Swagger docs | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |
| phpMyAdmin | http://localhost:8080 |

---

## API Endpoints

### Authentication
| Method | Route | Auth | Description |
|---|---|---|---|
| POST | `/auth/register` | Public | Register new user |
| POST | `/auth/login` | Public | Login → JWT token |

### Products (Public)
| Method | Route | Description |
|---|---|---|
| GET | `/products` | List all products |
| GET | `/products/{id}` | Get product detail |

### Cart (Public + Guest support)
| Method | Route | Description |
|---|---|---|
| POST | `/cart/add` | Add item to cart |
| PATCH | `/cart/update-qty` | Update item quantity |

### Orders (Protected)
| Method | Route | Description |
|---|---|---|
| POST | `/orders/checkout` | Checkout cart → create orders |
| GET | `/orders/history` | View order history |

### Admin (Admin only)
| Method | Route | Description |
|---|---|---|
| GET | `/admin/users` | List all users |
| GET | `/admin/orders` | List all orders |
| GET | `/admin/products` | List all products |

### Inventory (Admin only)
| Method | Route | Description |
|---|---|---|
| POST | `/inventory/product` | Create product + upload image |
| PUT | `/inventory/product/{id}` | Update product + replace image |
| DELETE | `/inventory/product/{id}` | Delete product + Cloudinary image |

---

## Authentication

Use `Authorization: Bearer <token>` header for protected endpoints.

Example:
```bash
# Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"john","password":"secret123","shipping_address":"123 Main St"}'

# Login → get token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"secret123"}'
```

---

## Creating an Admin User

After running migrations, manually set `is_admin = 1` for a user via phpMyAdmin or MySQL CLI:

```sql
UPDATE users SET is_admin = 1 WHERE email = 'admin@blockfusevintage.com';
```

---

## Running Migrations

```bash
# Apply all migrations
docker compose exec app alembic upgrade head

# Generate a new migration (after model changes)
docker compose exec app alembic revision --autogenerate -m "your message"

# Rollback one step
docker compose exec app alembic downgrade -1
```

---

## Environment Variables

See `.env.example` for all required variables:
- `DATABASE_URL` — MySQL connection string
- `JWT_SECRET_KEY` — Random secret (at least 64 chars)
- `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`
- `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`
- `ENVIRONMENT` — `development` or `production`

---

## Production Server

Gunicorn is configured via `gunicorn.conf.py`:
- Workers: `(2 * CPU cores) + 1`
- Worker class: `uvicorn.workers.UvicornWorker`
- Bind: `0.0.0.0:8000`
- Timeout: 120s
- No debug mode

---

## Deployment

Deploy to any cloud platform supporting Docker:
- **Railway** / **Render** / **Fly.io** — push Docker image
- **VPS** — `docker compose up -d` on your server

Set all environment variables in your hosting platform's dashboard.
