from sqlalchemy import Column, Integer, Boolean, ForeignKey
from app.core.database import Base


class UserPermission(Base):
    __tablename__ = "user_permissions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )

    location = Column(Boolean, nullable=False, default=False)
    camera = Column(Boolean, nullable=False, default=False)
    microphone = Column(Boolean, nullable=False, default=False)
    notifications = Column(Boolean, nullable=False, default=False)