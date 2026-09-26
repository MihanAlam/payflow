# PayFlow — Merchant Payment Analytics Platform

PayFlow is a backend API for a merchant payments dashboard: businesses can
process transactions, issue full or partial refunds, and see revenue and
fraud analytics — built around the concepts that real payment processors
(Stripe, Nuvei, etc.) use in production.

This project grew out of hands-on experience with merchant/payment
processing as a Nuvei partner, applied here as an actual backend system
rather than a tutorial CRUD app.

## Why this project is more than a CRUD app

Most student projects stop at "create/read/update/delete." PayFlow
implements four concepts that separate toy payment demos from how real
processors are built:

1. **Idempotency keys** — every transaction request carries a client-generated
   idempotency key. If a client's request times out and retries, the API
   returns the *original* transaction instead of double-charging the
   customer. See `backend/app/routers/transactions.py`.
2. **Partial refund accounting** — refunds are tracked as their own ledger
   against a transaction, so multiple partial refunds can never exceed the
   original amount, and transaction status correctly moves through
   `completed → partially_refunded → refunded`. See
   `backend/app/routers/refunds.py`.
3. **Explainable, rule-based fraud scoring** — transactions are scored
   against explicit rules (unusual amount, transaction velocity), each of
   which is logged as a `FraudFlag` row with a human-readable reason. This
   is deliberately not a black-box model: in an interview you can explain
   exactly why any transaction was flagged. See `backend/app/core/fraud.py`.
4. **Webhook event log with a retry-ready state machine** — every completed
   transaction emits a `WebhookEvent` row with a delivery status
   (`pending → delivered/failed → dead_letter`) and an attempt counter.
   This models the state a background worker would operate on to actually
   deliver webhooks with retries and backoff. See `backend/app/models/models.py`.

## Tech stack

- **FastAPI** (Python) — REST API framework
- **SQLAlchemy** — ORM, works against SQLite (zero-setup demo) or PostgreSQL (production)
- **JWT auth** (`python-jose` + `passlib`/bcrypt) — merchant login/session
- **Docker Compose** — one-command spin-up with PostgreSQL

## Project structure

```
payflow/
├── backend/
│   ├── app/
│   │   ├── core/          # database, security, auth deps, fraud scoring
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/         # Pydantic request/response schemas
│   │   ├── routers/         # auth, transactions, refunds, dashboard
│   │   └── main.py           # FastAPI app entrypoint
│   ├── seed.py                # generates a demo merchant + 150 fake transactions
│   ├── requirements.txt
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## Running it

### Option A — quick local run (SQLite, no Docker needed)

```bash
cd backend
pip install -r requirements.txt
python seed.py              # creates demo@payflow.dev / demopassword123 with 150 fake transactions
uvicorn app.main:app --reload
```

API docs (interactive): http://localhost:8000/docs

### Option B — Docker Compose (PostgreSQL, closer to production)

```bash
docker-compose up --build
```

Then, in a separate terminal, seed the Postgres database:
```bash
docker-compose exec backend python seed.py
```

## API walkthrough

```bash
# 1. Log in (demo credentials from seed.py)
curl -X POST http://localhost:8000/auth/login \
  -d "username=demo@payflow.dev&password=demopassword123" \
  -H "Content-Type: application/x-www-form-urlencoded"
# -> { "access_token": "...", "token_type": "bearer" }

# 2. Create a transaction (idempotent on idempotency_key)
curl -X POST http://localhost:8000/transactions \
  -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"idempotency_key":"order-123","amount":150.00,"customer_email":"buyer@example.com"}'

# 3. Issue a partial refund
curl -X POST http://localhost:8000/refunds \
  -H "Authorization: Bearer <TOKEN>" -H "Content-Type: application/json" \
  -d '{"transaction_id":"<TXN_ID>","amount":75.00,"reason":"customer request"}'

# 4. Dashboard summary
curl http://localhost:8000/dashboard/summary -H "Authorization: Bearer <TOKEN>"
```

## What's next (not yet built)

- **Frontend dashboard** (React + charts) consuming this API
- **Background worker** to actually deliver webhook events with retry/backoff,
  using the `WebhookEvent` state machine that already exists
- **Alembic migrations** in place of `Base.metadata.create_all` for real schema versioning
- **Rate limiting** on the transaction-creation endpoint

## A note on scope

This is a simulation for portfolio/learning purposes — it does not connect
to a real payment processor or move real money. The idempotency, refund
accounting, fraud-flagging, and webhook patterns are real production
patterns, applied to synthetic data.
