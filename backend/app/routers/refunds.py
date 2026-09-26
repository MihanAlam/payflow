from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_merchant
from app.models.models import Merchant, Refund, RefundStatus, Transaction, TransactionStatus
from app.schemas.schemas import RefundCreate, RefundOut

router = APIRouter(prefix="/refunds", tags=["refunds"])


@router.post("", response_model=RefundOut, status_code=201)
def create_refund(
    payload: RefundCreate,
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant),
):
    txn = (
        db.query(Transaction)
        .filter(Transaction.id == payload.transaction_id, Transaction.merchant_id == merchant.id)
        .first()
    )
    if not txn:
        raise HTTPException(status_code=404, detail="Transaction not found")
    if txn.status not in (TransactionStatus.completed, TransactionStatus.partially_refunded):
        raise HTTPException(status_code=400, detail=f"Cannot refund a transaction with status {txn.status.value}")

    already_refunded = sum(
        r.amount for r in txn.refunds if r.status == RefundStatus.completed
    )
    remaining = txn.amount - already_refunded
    if payload.amount > remaining:
        raise HTTPException(
            status_code=400,
            detail=f"Refund amount {payload.amount:.2f} exceeds remaining refundable balance {remaining:.2f}",
        )

    refund = Refund(
        transaction_id=txn.id,
        amount=payload.amount,
        reason=payload.reason,
        status=RefundStatus.completed,  # simulated instant settlement for the demo
    )
    db.add(refund)

    new_total_refunded = already_refunded + payload.amount
    txn.status = (
        TransactionStatus.refunded
        if new_total_refunded >= txn.amount
        else TransactionStatus.partially_refunded
    )

    db.commit()
    db.refresh(refund)
    return refund


@router.get("", response_model=list[RefundOut])
def list_refunds(
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant),
):
    return (
        db.query(Refund)
        .join(Transaction)
        .filter(Transaction.merchant_id == merchant.id)
        .order_by(Refund.created_at.desc())
        .all()
    )
