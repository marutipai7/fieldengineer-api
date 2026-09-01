from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.utils.auth_utils import (
    get_current_user_mobile,
    get_current_user_object
)
from app.profile.models import User

from .models import PaymentHistory
from .schemas import PaymentHistoryCreate, PaymentHistoryResponse

from app.payment_method.models import (
    UpiPayment,
    NetBankingPayment,
    CardPayment
)

from app.payment_method.schemas import (
    PaymentCreate,
    PaymentUpdate,
    PaymentDelete
)

from app.payment_method.schemas import (
    PaymentCreate,
    PaymentUpdate,
    PaymentDelete,
    VerifyUpiRequest,
    VerifyBankRequest,
    VerifyCardRequest
)

from app.payment_method.schemas import (
    PaymentHistoryCreate,
    PaymentHistoryResponse,
)

router = APIRouter(
    prefix="/payment",
    tags=["Payment"]
)


def get_current_user(
    mobile_number: str,
    db: Session
):
    user = db.execute(
        select(User).where(
            User.mobile_number == mobile_number
        )
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user



def reset_primary_payment(user_id: int, db: Session):

    db.query(CardPayment).filter(
        CardPayment.user_id == user_id
    ).update(
        {"is_primary": False},
        synchronize_session=False
    )

    db.query(UpiPayment).filter(
        UpiPayment.user_id == user_id
    ).update(
        {"is_primary": False},
        synchronize_session=False
    )

    db.query(NetBankingPayment).filter(
        NetBankingPayment.user_id == user_id
    ).update(
        {"is_primary": False},
        synchronize_session=False
    )

    


@router.post("")
async def add_payment(
    payload: PaymentCreate,
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):

    user = get_current_user(
        current_user_mobile,
        db
    )
    if payload.is_primary:
       reset_primary_payment(user.id, db)

    if payload.payment_type == "upi":

        payment = UpiPayment(
            user_id=user.id,
            upi_id=payload.upi_id,
            is_primary=payload.is_primary
        )

    elif payload.payment_type == "net_banking":

        payment = NetBankingPayment(
            user_id=user.id,
            bank_name=payload.bank_name,
            account_holder_name=payload.account_holder_name,
            account_number=payload.account_number,
            ifsc_code=payload.ifsc_code,
            is_primary=payload.is_primary
        )

    elif payload.payment_type == "card":

        payment = CardPayment(
            user_id=user.id,
            card_holder_name=payload.card_holder_name,
            card_number=payload.card_number,
            expiry_month=payload.expiry_month,
            expiry_year=payload.expiry_year,
            cvv=payload.cvv,
            card_type=payload.card_type,
            is_primary=payload.is_primary
        )

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment type"
        )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment method added successfully",
        "payment_id": payment.id
    }

@router.post("/verify-upi")
async def verify_upi(
    payload: VerifyUpiRequest,
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):

    user = get_current_user(current_user_mobile, db)

    payment = db.execute(
        select(UpiPayment).where(
            UpiPayment.id == payload.payment_id,
            UpiPayment.user_id == user.id
        )
    ).scalars().first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="UPI payment not found"
        )

    payment.is_verified = True

    db.commit()
    db.refresh(payment)

    return {
        "message": "UPI verified successfully",
        "payment_id": payment.id,
        "is_verified": payment.is_verified
    }

@router.post("/verify-bank")
async def verify_bank(
    payload: VerifyBankRequest,
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):

    user = get_current_user(current_user_mobile, db)

    payment = db.execute(
        select(NetBankingPayment).where(
            NetBankingPayment.id == payload.payment_id,
            NetBankingPayment.user_id == user.id
        )
    ).scalars().first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Bank account not found"
        )

    payment.is_verified = True

    db.commit()
    db.refresh(payment)

    return {
        "message": "Bank verified successfully",
        "payment_id": payment.id,
        "is_verified": payment.is_verified
    }

@router.post("/verify-card")
async def verify_card(
    payload: VerifyCardRequest,
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):

    user = get_current_user(current_user_mobile, db)

    payment = db.execute(
        select(CardPayment).where(
            CardPayment.id == payload.payment_id,
            CardPayment.user_id == user.id
        )
    ).scalars().first()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Card not found"
        )

    payment.is_verified = True

    db.commit()
    db.refresh(payment)

    return {
        "message": "Card verified successfully",
        "payment_id": payment.id,
        "is_verified": payment.is_verified
    }

@router.get("")
async def get_payments(
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):
    user = get_current_user(
        current_user_mobile,
        db
    )
   

    upi = db.execute(
        select(UpiPayment).where(
            UpiPayment.user_id == user.id
        )
    ).scalars().all()

    net_banking = db.execute(
        select(NetBankingPayment).where(
            NetBankingPayment.user_id == user.id
        )
    ).scalars().all()

    card = db.execute(
        select(CardPayment).where(
            CardPayment.user_id == user.id
        )
    ).scalars().all()

    return {
        "upi": [
            {
                "id": item.id,
                "upi_id": item.upi_id,
                "is_primary": item.is_primary,
                "is_verified": item.is_verified
            }
            for item in upi
        ],

        "net_banking": [
            {
                "id": item.id,
                "bank_name": item.bank_name,
                "account_holder_name": item.account_holder_name,
                "account_number": item.account_number,
                "ifsc_code": item.ifsc_code,
                "is_primary": item.is_primary,
                "is_verified": item.is_verified
            }
            for item in net_banking
        ],

        "card": [
            {
                "id": item.id,
                "card_holder_name": item.card_holder_name,
                "card_number": item.card_number,
                "expiry_month": item.expiry_month,
                "expiry_year": item.expiry_year,
                "card_type": item.card_type,
                "is_primary": item.is_primary,
                "is_verified": item.is_verified
            }
            for item in card
        ]
    }


@router.put("/{payment_id}")
async def update_payment(
    payment_id: int,
    payload: PaymentUpdate,
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):

    user = get_current_user(
        current_user_mobile,
        db
    )

    if payload.is_primary:
       reset_primary_payment(user.id, db)

    if payload.payment_type == "upi":

        payment = db.execute(
            select(UpiPayment).where(
                UpiPayment.id == payment_id,
                UpiPayment.user_id == user.id
            )
        ).scalars().first()

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="UPI payment not found"
            )

        payment.upi_id = payload.upi_id
        payment.is_primary = payload.is_primary

    elif payload.payment_type == "net_banking":

        payment = db.execute(
            select(NetBankingPayment).where(
                NetBankingPayment.id == payment_id,
                NetBankingPayment.user_id == user.id
            )
        ).scalars().first()

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Net Banking payment not found"
            )

        payment.bank_name = payload.bank_name
        payment.account_holder_name = payload.account_holder_name
        payment.account_number = payload.account_number
        payment.ifsc_code = payload.ifsc_code
        payment.is_primary = payload.is_primary

    elif payload.payment_type == "card":

        payment = db.execute(
            select(CardPayment).where(
                CardPayment.id == payment_id,
                CardPayment.user_id == user.id
            )
        ).scalars().first()

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Card payment not found"
            )

        payment.card_holder_name = payload.card_holder_name
        payment.card_number = payload.card_number
        payment.expiry_month = payload.expiry_month
        payment.expiry_year = payload.expiry_year
        payment.cvv = payload.cvv
        payment.card_type = payload.card_type
        payment.is_primary = payload.is_primary

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment type"
        )

    db.commit()
    db.refresh(payment)

    return {
        "message": "Payment updated successfully",
        "payment_id": payment.id
    }


@router.delete("/{payment_id}")
async def delete_payment(
    payment_id: int,
    payload: PaymentDelete,
    current_user_mobile: str = Depends(get_current_user_mobile),
    db: Session = Depends(get_db)
):

    user = get_current_user(
        current_user_mobile,
        db
    )

    if payload.payment_type == "upi":

        payment = db.execute(
            select(UpiPayment).where(
                UpiPayment.id == payment_id,
                UpiPayment.user_id == user.id
            )
        ).scalars().first()

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="UPI payment not found"
            )

    elif payload.payment_type == "net_banking":

        payment = db.execute(
            select(NetBankingPayment).where(
                NetBankingPayment.id == payment_id,
                NetBankingPayment.user_id == user.id
            )
        ).scalars().first()

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Net Banking payment not found"
            )

    elif payload.payment_type == "card":

        payment = db.execute(
            select(CardPayment).where(
                CardPayment.id == payment_id,
                CardPayment.user_id == user.id
            )
        ).scalars().first()

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Card payment not found"
            )

    else:
        raise HTTPException(
            status_code=400,
            detail="Invalid payment type"
        )

    db.delete(payment)
    db.commit()

    return {
        "message": "Payment deleted successfully"
    }

@router.post(
    "/history",
    response_model=PaymentHistoryResponse
)
def create_payment_history(
    data: PaymentHistoryCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_object)
):

    user, profile = current_user

    payment = PaymentHistory(
        user_id=user.id,

    amount=data.amount,

    status=data.status,

    transaction_reference=data.transaction_reference,

    upi_payment_id=data.upi_payment_id,

    card_payment_id=data.card_payment_id,

    net_banking_payment_id=data.net_banking_payment_id,
    )

    try:
        db.add(payment)
        db.commit()
        db.refresh(payment)

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Failed to create payment history"
        )from e

    return payment


@router.get(
    "/history",
    response_model=list[PaymentHistoryResponse]
)
def get_payment_history(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_object)
):
    user, profile = current_user

    stmt = (
        select(PaymentHistory)
        .where(PaymentHistory.user_id == user.id)
        .order_by(PaymentHistory.created_at.desc())
    )

    result = db.execute(stmt)

    history = result.scalars().all()

    return history


@router.get(
    "/history/{history_id}",
    response_model=PaymentHistoryResponse
)
def get_payment_history_by_id(
    history_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_object)
):
    user, profile = current_user

    stmt = (
        select(PaymentHistory)
        .where(
            PaymentHistory.id == history_id,
            PaymentHistory.user_id == user.id
        )
    )

    result = db.execute(stmt)

    payment = result.scalar_one_or_none()

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment history not found"
        )

    return payment