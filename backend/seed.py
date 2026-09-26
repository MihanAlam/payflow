"""
Seeds the database with a demo merchant and ~150 fake transactions spread
over the last 30 days, including a few refunds and a few intentionally
high-amount transactions so the fraud flags and dashboard charts have
something real to show.

Run with:  python seed.py
"""
import json
import random
import uuid
from datetime import datetime, timedelta, timezone

from faker import Faker

from app.core.database import Base, SessionLocal, engine
from app.core.fraud import score_transaction, FLAG_THRESHOLD
from app.core.security import hash_password
from app.models.models import (
    FraudFlag, Merchant, Refund, RefundStatus, Transaction, TransactionStatus,
    WebhookEvent, WebhookStatus,
)

fake = Faker()

DEMO_EMAIL = "demo@payflow.dev"
DEMO_PASSWORD = "demopassword123"


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        merchant = db.query(Merchant).filter(Merchant.email == DEMO_EMAIL).first()
        if not merchant:
            merchant = Merchant(
                business_name="Northgate Hardware Co.",
                email=DEMO_EMAIL,
                hashed_password=hash_password(DEMO_PASSWORD),
            )
            db.add(merchant)
            db.commit()
            db.refresh(merchant)
            print(f"Created demo merchant: {DEMO_EMAIL} / {DEMO_PASSWORD}")
        else:
            print("Demo merchant already exists, adding more transactions to it.")

        now = datetime.now(timezone.utc)
        created_txns = []

        for _ in range(150):
            days_ago = random.randint(0, 30)
            created_at = now - timedelta(days=days_ago, hours=random.randint(0, 23))

            # Occasionally simulate a suspiciously large transaction so
            # fraud flags actually have something to catch.
            if random.random() < 0.08:
                amount = round(random.uniform(2000, 6000), 2)
            else:
                amount = round(random.uniform(15, 450), 2)

            score, triggered_rules = score_transaction(db, merchant.id, amount)
            is_flagged = score >= FLAG_THRESHOLD

            txn = Transaction(
                merchant_id=merchant.id,
                idempotency_key=str(uuid.uuid4()),
                amount=amount,
                currency="CAD",
                customer_email=fake.email(),
                status=TransactionStatus.completed,
                is_flagged=is_flagged,
                fraud_score=score,
                created_at=created_at,
            )
            db.add(txn)
            db.flush()
            created_txns.append(txn)

            for rule_name, detail in triggered_rules:
                db.add(FraudFlag(transaction_id=txn.id, rule_triggered=rule_name, detail=detail))

            db.add(WebhookEvent(
                merchant_id=merchant.id,
                event_type="transaction.completed",
                payload=json.dumps({"transaction_id": txn.id, "amount": amount}),
                status=random.choice([WebhookStatus.delivered, WebhookStatus.delivered, WebhookStatus.pending]),
                created_at=created_at,
            ))

        db.commit()

        # Refund ~10% of transactions, fully or partially.
        for txn in random.sample(created_txns, k=max(1, len(created_txns) // 10)):
            partial = random.random() < 0.4
            refund_amount = round(txn.amount * random.uniform(0.3, 0.6), 2) if partial else txn.amount

            db.add(Refund(
                transaction_id=txn.id,
                amount=refund_amount,
                reason=random.choice(["customer request", "duplicate charge", "product return", "service issue"]),
                status=RefundStatus.completed,
            ))
            txn.status = TransactionStatus.partially_refunded if partial else TransactionStatus.refunded

        db.commit()
        print(f"Seeded {len(created_txns)} transactions with refunds and fraud flags.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
