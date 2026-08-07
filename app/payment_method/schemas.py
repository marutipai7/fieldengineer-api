from typing import Optional, Literal
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PaymentBase(BaseModel):
    payment_type: Literal["upi", "net_banking", "card"]
    is_primary: Optional[bool] = False


# ------------------------
# Create Payment
# ------------------------

class PaymentCreate(PaymentBase):

    # UPI
    upi_id: Optional[str] = None

    # Net Banking
    bank_name: Optional[str] = None
    account_holder_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None

    # Card
    card_holder_name: Optional[str] = None
    card_number: Optional[str] = None
    expiry_month: Optional[str] = None
    expiry_year: Optional[str] = None
    cvv: Optional[str] = None
    card_type: Optional[str] = None


# ------------------------
# Update Payment
# ------------------------

class PaymentUpdate(PaymentBase):

    # UPI
    upi_id: Optional[str] = None

    # Net Banking
    bank_name: Optional[str] = None
    account_holder_name: Optional[str] = None
    account_number: Optional[str] = None
    ifsc_code: Optional[str] = None

    # Card
    card_holder_name: Optional[str] = None
    card_number: Optional[str] = None
    expiry_month: Optional[str] = None
    expiry_year: Optional[str] = None
    cvv: Optional[str] = None
    card_type: Optional[str] = None


# ------------------------
# Delete Payment
# ------------------------

class PaymentDelete(BaseModel):
    payment_type: Literal[
        "upi",
        "net_banking",
        "card"
    ]


# ------------------------
# Response
# ------------------------

class PaymentResponse(BaseModel):

    id: int
    payment_type: str
    is_primary: bool
    is_verified: bool

    class Config:
        from_attributes = True

class VerifyUpiRequest(BaseModel):
    payment_id: int


class VerifyBankRequest(BaseModel):
    payment_id: int


class VerifyCardRequest(BaseModel):
    payment_id: int
    
# ------------------------
# Transaction_History
# ------------------------

class PaymentHistoryBase(BaseModel):
    amount: float
    status: str
    transaction_reference: str | None = None


class PaymentHistoryCreate(PaymentHistoryBase):
    upi_payment_id: Optional[int] = None
    card_payment_id: Optional[int] = None
    net_banking_payment_id: Optional[int] = None


class PaymentHistoryResponse(PaymentHistoryBase):
    id: int
    user_id: int

    upi_payment_id: Optional[int] = None
    card_payment_id: Optional[int] = None
    net_banking_payment_id: Optional[int] = None

    created_at: datetime

    class Config:
        from_attributes = True