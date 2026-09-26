from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.models.models import Merchant
from app.schemas.schemas import MerchantCreate, MerchantOut, Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=MerchantOut, status_code=status.HTTP_201_CREATED)
def register(payload: MerchantCreate, db: Session = Depends(get_db)):
    existing = db.query(Merchant).filter(Merchant.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    merchant = Merchant(
        business_name=payload.business_name,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(merchant)
    db.commit()
    db.refresh(merchant)
    return merchant


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm uses "username" as the field name; we treat it as email.
    merchant = db.query(Merchant).filter(Merchant.email == form_data.username).first()
    if not merchant or not verify_password(form_data.password, merchant.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = create_access_token({"sub": merchant.id})
    return Token(access_token=token)
