"""
Rule-based fraud scoring.

This is intentionally NOT a black-box ML model -- for an interview, being
able to explain exactly why a transaction was flagged (which rule fired,
with what evidence) is more valuable than a model you can't walk through.
Each rule contributes to a 0-1 score; scores above FLAG_THRESHOLD flag the
transaction and write a FraudFlag row explaining why.

This is structured so a real model (e.g. a small sklearn classifier
trained on transaction features) could be swapped in later as one more
signal alongside these rules, without changing the calling code.
"""
from datetime import datetime, timedelta, timezone
from typing import List, Tuple

from sqlalchemy.orm import Session

from app.models.models import Transaction

FLAG_THRESHOLD = 0.6

# Rule 1: unusually high amount relative to typical transaction size.
HIGH_AMOUNT_THRESHOLD = 2000.0
VERY_HIGH_AMOUNT_THRESHOLD = 4000.0

# Rule 2: velocity -- too many transactions from the same merchant in a
# short window can indicate a compromised account or testing stolen cards.
VELOCITY_WINDOW_MINUTES = 10
VELOCITY_COUNT_THRESHOLD = 5


def score_transaction(db: Session, merchant_id: str, amount: float) -> Tuple[float, List[Tuple[str, str]]]:
    """Returns (score, [(rule_name, detail), ...]) for the triggered rules."""
    score = 0.0
    triggered: List[Tuple[str, str]] = []

    if amount >= HIGH_AMOUNT_THRESHOLD:
        score += 0.5
        triggered.append((
            "high_amount",
            f"Amount {amount:.2f} exceeds threshold {HIGH_AMOUNT_THRESHOLD:.2f}",
        ))
    if amount >= VERY_HIGH_AMOUNT_THRESHOLD:
        score += 0.2
        triggered.append((
            "very_high_amount",
            f"Amount {amount:.2f} exceeds extreme threshold {VERY_HIGH_AMOUNT_THRESHOLD:.2f}",
        ))

    window_start = datetime.now(timezone.utc) - timedelta(minutes=VELOCITY_WINDOW_MINUTES)
    recent_count = (
        db.query(Transaction)
        .filter(Transaction.merchant_id == merchant_id, Transaction.created_at >= window_start)
        .count()
    )
    if recent_count >= VELOCITY_COUNT_THRESHOLD:
        score += 0.4
        triggered.append((
            "velocity",
            f"{recent_count} transactions in the last {VELOCITY_WINDOW_MINUTES} minutes",
        ))

    return min(score, 1.0), triggered
