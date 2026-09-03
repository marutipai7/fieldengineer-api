from sqlalchemy import Column, Integer, Boolean, ForeignKey
from app.core.database import Base


class UserPermission(Base):
    __tablename__ = "user_permissions"
    id = Column(
        Integer,
        primary_key=True,
        autoincrement=True,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    location = Column(Boolean, nullable=False, default=False)
    communication = Column(Boolean, nullable=False, default=False)
    notifications = Column(Boolean, nullable=False, default=False)
    camera = Column(Boolean, nullable=False, default=False)
    media = Column(Boolean, nullable=False, default=False)
    audio = Column(Boolean, nullable=False, default=False)
    payment = Column(Boolean, nullable=False, default=False)
    security = Column(Boolean, nullable=False, default=False)
    network = Column(Boolean, nullable=False, default=False)
    device = Column(Boolean, nullable=False, default=False)