from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import Base, engine
from app.routers import auth, dashboard, refunds, transactions

# Creates tables on startup if they don't exist. For a real production
# deploy you'd use Alembic migrations instead -- noted in the README.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="PayFlow API",
    description="Merchant payment analytics platform -- transactions, refunds, fraud flags, webhooks.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your frontend's origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(refunds.router)
app.include_router(dashboard.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "PayFlow API"}


@app.get("/health")
def health():
    return {"status": "healthy"}
