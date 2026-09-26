from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_merchant
from app.models.models import (
    Merchant, Refund, RefundStatus, Transaction, TransactionStatus, WebhookEvent, WebhookStatus,
)
from app.schemas.schemas import DashboardSummary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(
    db: Session = Depends(get_db),
    merchant: Merchant = Depends(get_current_merchant),
):
    txns = db.query(Transaction).filter(Transaction.merchant_id == merchant.id).all()
    txn_ids = [t.id for t in txns]

    refunds = (
        db.query(Refund).filter(Refund.transaction_id.in_(txn_ids)).all()
        if txn_ids else []
    )
    completed_refunds = [r for r in refunds if r.status == RefundStatus.completed]

    pending_webhooks = (
        db.query(WebhookEvent)
        .filter(WebhookEvent.merchant_id == merchant.id, WebhookEvent.status == WebhookStatus.pending)
        .count()
    )

    revenue_by_day = defaultdict(float)
    for t in txns:
        if t.status in (TransactionStatus.completed, TransactionStatus.partially_refunded, TransactionStatus.refunded):
            day = t.created_at.strftime("%Y-%m-%d") if t.created_at else "unknown"
            revenue_by_day[day] += t.amount

    return DashboardSummary(
        total_revenue=sum(t.amount for t in txns if t.status != TransactionStatus.failed),
        total_transactions=len(txns),
        total_refunded=sum(r.amount for r in completed_refunds),
        refund_count=len(completed_refunds),
        flagged_count=sum(1 for t in txns if t.is_flagged),
        pending_webhooks=pending_webhooks,
        revenue_by_day=[{"date": d, "revenue": round(v, 2)} for d, v in sorted(revenue_by_day.items())],
    )
