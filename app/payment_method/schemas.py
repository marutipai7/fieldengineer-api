from typing import Optional, Literal
from pydantic import BaseModel


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