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
        index=True,
    )

    location = Column(Boolean, default=False, nullable=False)
    camera = Column(Boolean, default=False, nullable=False)
    microphone = Column(Boolean, default=False, nullable=False)
    notifications = Column(Boolean, default=False, nullable=False)
    