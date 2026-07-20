from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from datetime import datetime


from app.core.database import Base



#UPI Payment Model


class UpiPayment(Base):
    __tablename__ = "upi_payments"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    upi_id = Column(String(100), nullable=False)

    is_primary = Column(Boolean, default=False)

    is_verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # user = relationship("User", back_populates="upi_payments")
    user = relationship("User")

#Net Banking Model

class NetBankingPayment(Base):
    __tablename__ = "net_banking_payments"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    bank_name = Column(String(100), nullable=False)

    account_holder_name = Column(String(150))

    account_number = Column(String(50))

    ifsc_code = Column(String(20))

    is_primary = Column(Boolean, default=False)

    is_verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # user = relationship("User", back_populates="net_banking_payments")
    user = relationship("User")




#Card Payment Model



class CardPayment(Base):
    __tablename__ = "card_payments"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    card_holder_name = Column(String(150), nullable=False)

    card_number = Column(String(30), nullable=False)

    expiry_month = Column(String(2), nullable=False)

    expiry_year = Column(String(4), nullable=False)

    cvv = Column(String(4), nullable=False)

    card_type = Column(String(30))

    is_primary = Column(Boolean, default=False)

    is_verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # user = relationship("User", back_populates="card_payments")
    user = relationship("User")