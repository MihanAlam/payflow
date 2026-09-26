"""
Core data models for PayFlow.

Design notes (worth mentioning in interviews):
- Transaction.idempotency_key is unique + indexed: this is how real payment
  APIs (Stripe, Nuvei, etc.) prevent double-charging when a client retries
  a request after a timeout. Same key = same transaction returned, not a
  new one created.
- WebhookEvent models an outbound event log with a delivery status and
  attempt count, which is the basis for a retry / dead-letter mechanism.
- FraudFlag is separate from Transaction so a transaction can accumulate
  multiple signals over time without mutating the original record.
"""
import enum
import uuid

from sqlalchemy import (
    Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


def gen_uuid() -> str:
    return str(uuid.uuid4())


class TransactionStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"
    partially_refunded = "partially_refunded"


class RefundStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"


class WebhookStatus(str, enum.Enum):
    pending = "pending"
    delivered = "delivered"
    failed = "failed"
    dead_letter = "dead_letter"


class Merchant(Base):
    __tablename__ = "merchants"

    id = Column(String, primary_key=True, default=gen_uuid)
    business_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transactions = relationship("Transaction", back_populates="merchant")
    webhook_events = relationship("WebhookEvent", back_populates="merchant")


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(String, primary_key=True, default=gen_uuid)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)

    # Prevents duplicate charges on client retry -- see module docstring.
    idempotency_key = Column(String, unique=True, index=True, nullable=False)

    amount = Column(Float, nullable=False)
    currency = Column(String, default="CAD")
    customer_email = Column(String, nullable=True)
    status = Column(Enum(TransactionStatus), default=TransactionStatus.pending)

    is_flagged = Column(Boolean, default=False)
    fraud_score = Column(Float, default=0.0)  # 0-1, higher = riskier

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    merchant = relationship("Merchant", back_populates="transactions")
    refunds = relationship("Refund", back_populates="transaction")
    fraud_flags = relationship("FraudFlag", back_populates="transaction")


class Refund(Base):
    __tablename__ = "refunds"

    id = Column(String, primary_key=True, default=gen_uuid)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)
    amount = Column(Float, nullable=False)
    reason = Column(String, nullable=True)
    status = Column(Enum(RefundStatus), default=RefundStatus.pending)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transaction = relationship("Transaction", back_populates="refunds")


class FraudFlag(Base):
    __tablename__ = "fraud_flags"

    id = Column(String, primary_key=True, default=gen_uuid)
    transaction_id = Column(String, ForeignKey("transactions.id"), nullable=False)
    rule_triggered = Column(String, nullable=False)  # e.g. "high_amount", "velocity"
    detail = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    transaction = relationship("Transaction", back_populates="fraud_flags")


class WebhookEvent(Base):
    """
    Outbound event log. In production this would drive a background worker
    that POSTs to the merchant's registered URL and retries with backoff;
    here it models the state machine (pending -> delivered/failed ->
    dead_letter after max attempts) that such a worker would operate on.
    """
    __tablename__ = "webhook_events"

    id = Column(String, primary_key=True, default=gen_uuid)
    merchant_id = Column(String, ForeignKey("merchants.id"), nullable=False)
    event_type = Column(String, nullable=False)  # e.g. "transaction.completed"
    payload = Column(Text, nullable=False)  # JSON-serialized snapshot
    status = Column(Enum(WebhookStatus), default=WebhookStatus.pending)
    attempts = Column(Integer, default=0)
    max_attempts = Column(Integer, default=5)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_attempt_at = Column(DateTime(timezone=True), nullable=True)

    merchant = relationship("Merchant", back_populates="webhook_events")
