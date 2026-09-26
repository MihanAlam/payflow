from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr, Field


# ---------- Auth ----------

class MerchantCreate(BaseModel):
    business_name: str
    email: EmailStr
    password: str = Field(min_length=8)


class MerchantOut(BaseModel):
    id: str
    business_name: str
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Transactions ----------

class TransactionCreate(BaseModel):
    idempotency_key: str
    amount: float = Field(gt=0)
    currency: str = "CAD"
    customer_email: Optional[EmailStr] = None


class TransactionOut(BaseModel):
    id: str
    amount: float
    currency: str
    customer_email: Optional[str]
    status: str
    is_flagged: bool
    fraud_score: float
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Refunds ----------

class RefundCreate(BaseModel):
    transaction_id: str
    amount: float = Field(gt=0)
    reason: Optional[str] = None


class RefundOut(BaseModel):
    id: str
    transaction_id: str
    amount: float
    reason: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ---------- Dashboard ----------

class DashboardSummary(BaseModel):
    total_revenue: float
    total_transactions: int
    total_refunded: float
    refund_count: int
    flagged_count: int
    pending_webhooks: int
    revenue_by_day: List[dict]
