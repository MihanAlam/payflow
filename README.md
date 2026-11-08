# PayFlow — Merchant Payment Analytics Platform

A simulated merchant payments platform with a Python/FastAPI backend and React dashboard. I built it to explore transaction processing and reporting, drawing on my experience with merchant onboarding as a Nuvei referral partner.

**Portfolio project:** PayFlow uses synthetic data. It does not connect to a payment processor or move real money.

## Features

- Merchant authentication with JWT sessions.
- Idempotent transaction requests, so a retried request returns the original transaction.
- Full and partial refunds, tracked against the original transaction amount.
- Rule-based fraud scoring with recorded reasons for flagged transactions.
- Webhook event tracking, including delivery status and attempt counts.
- React dashboard with an overview, revenue chart, and transaction ledger with refund controls.

The webhook event model records delivery state; a background worker for actual delivery and retries is still planned.

## Stack

- **Backend:** Python, FastAPI, SQLAlchemy, JWT authentication
- **Frontend:** React, Vite
- **Database:** SQLite for a local demo or PostgreSQL through Docker Compose
- **Development:** Git, Docker Compose

## Project structure

```text
payflow/
├── backend/
│   ├── app/
│   │   ├── core/       # database, security, auth dependencies, fraud scoring
│   │   ├── models/     # SQLAlchemy models
│   │   ├── schemas/    # request and response schemas
│   │   ├── routers/    # authentication, transactions, refunds, dashboard
│   │   └── main.py
│   ├── seed.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/           # React dashboard and Vite configuration
├── docker-compose.yml
└── README.md
```

## Run the backend locally

From the repository root:

```bash
cd backend
pip install -r requirements.txt
python seed.py
uvicorn app.main:app --reload
```

The seed script creates a demo merchant and 150 synthetic transactions. Demo login: `demo@payflow.dev` / `demopassword123`. These are local demo credentials, not a real account.

Open the interactive API documentation at [localhost:8000/docs](http://localhost:8000/docs).

### PostgreSQL with Docker Compose

From the repository root:

```bash
docker-compose up --build
```

In another terminal, seed the database:

```bash
docker-compose exec backend python seed.py
```

## Explore the code

- [React dashboard](frontend/src)
- [Frontend configuration](frontend/package.json) and [environment example](frontend/.env.example)
- [Transaction endpoints](backend/app/routers/transactions.py)
- [Refund endpoints](backend/app/routers/refunds.py)
- [Fraud scoring](backend/app/core/fraud.py)
- [Database models and webhook state](backend/app/models/models.py)

## Planned improvements

- Background webhook delivery with retries and backoff.
- Alembic migrations for database schema changes.
- Rate limiting on transaction creation.
