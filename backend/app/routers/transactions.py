import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_merchant
from app.core.fraud import score_transaction, FLAG_THRESHOLD
from app.models.models import (
    FraudFlag, Merchant, Transaction, TransactionStatus, WebhookEvent,
)
from app.schemas.schemas import TransactionCreate, TransactionOut

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", response_model=TransactionOut, status_code=201)
def create_transaction(
    payload: TransactionCreate,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant),
):
    # --- Idempotency check ---
    # If a client retries the same request (e.g. after a timeout on their
    # end), return the existing transaction instead of creating a duplicate
    # charge. This is the same pattern Stripe/Nuvei use in production.
    existing = (
        db.query(Transaction)
        .filter(Transaction.idempotency_key == payload.idempotency_key)
        .first()
    )
    if existing:
        return existing

    # --- Fraud scoring ---
    score, triggered_rules = score_transaction(db, merchant.id, payload.amount)
    is_flagged = score >= FLAG_THRESHOLD

    txn = Transaction(
        merchant_id=merchant.id,
        idempotency_key=payload.idempotency_key,
        amount=payload.amount,
        currency=payload.currency,
        customer_email=payload.customer_email,
        status=TransactionStatus.completed,
        is_flagged=is_flagged,
        fraud_score=score,
    )
    db.add(txn)
    db.flush()  # get txn.id before commit

    for rule_name, detail in triggered_rules:
        db.add(FraudFlag(transaction_id=txn.id, rule_triggered=rule_name, detail=detail))

    # --- Emit a webhook event (pending; a background worker would deliver it) ---
    event_payload = {
        "transaction_id": txn.id,
        "amount": txn.amount,
        "currency": txn.currency,
        "status": txn.status.value,
        "is_flagged": txn.is_flagged,
    }
    db.add(WebhookEvent(
        merchant_id=merchant.id,
        event_type="transaction.completed",
        payload=json.dumps(event_payload),
    ))

    db.commit()
    db.refresh(txn)
    return txn


@router.get("", response_model=list[TransactionOut])
def list_transactions(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant),
):
    return (
        db.query(Transaction)
        .filter(Transaction.merchant_id == merchant.id)
        .order_by(Transaction.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant),
):
    txn = (
        db.query(Transaction)
        .filter(Transaction.id == transaction_id, Transaction.merchant_id == merchant.id)
        .first()
    )
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return txn
