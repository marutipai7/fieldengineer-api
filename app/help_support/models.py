from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class IssueType(Base):
    __tablename__ = "issue_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)

    issues = relationship("Issue", back_populates="issue_type")


class Issue(Base):
    __tablename__ = "issues"

    id = Column(Integer, primary_key=True, index=True)

    issue_type_id = Column(
        Integer,
        ForeignKey("issue_types.id", ondelete="CASCADE"),
        nullable=False
    )

    name = Column(String(255), nullable=False)

    issue_type = relationship(
        "IssueType",
        back_populates="issues"
    )


class ReportIssue(Base):
    __tablename__ = "report_issues"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    issue_type_id = Column(
        Integer,
        ForeignKey("issue_types.id"),
        nullable=False
    )

    issue_id = Column(
        Integer,
        ForeignKey("issues.id"),
        nullable=False
    )

    description = Column(Text)

    attachment = Column(Text)

    status = Column(
        String(30),
        default="Submitted"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    user = relationship("User")

    issue_type = relationship("IssueType")

    issue = relationship("Issue")

