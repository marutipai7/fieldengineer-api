from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.database import get_db
from app.utils.auth_utils import get_current_user_email

from app.profile.models import User
from app.help_support.models import (
    IssueType,
    Issue,
    ReportIssue
)

from app.help_support.schemas import (
    ReportIssueCreateSchema
)

router = APIRouter(
    prefix="/help-support",
    tags=["Help Support"]
)

@router.get("/issue-types")
async def get_issue_types(
    db: Session = Depends(get_db)
):
    issue_types = db.execute(
        select(IssueType)
    ).scalars().all()

    return [
        {
            "id": issue_type.id,
            "name": issue_type.name
        }
        for issue_type in issue_types
    ]

@router.get("/issues/{issue_type_id}")
async def get_issues(
    issue_type_id: int,
    db: Session = Depends(get_db)
):

    issues = db.execute(
        select(Issue).where(
            Issue.issue_type_id == issue_type_id
        )
    ).scalars().all()

    return [
        {
            "id": issue.id,
            "name": issue.name
        }
        for issue in issues
    ]

@router.post("/report-issue")
async def report_issue(
    payload: ReportIssueCreateSchema,
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):

    user = db.execute(
        select(User).where(
            User.email == current_user_email
        )
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    issue_type = db.execute(
        select(IssueType).where(
            IssueType.id == payload.issue_type_id
        )
    ).scalars().first()

    if not issue_type:
        raise HTTPException(
            status_code=404,
            detail="Issue Type not found"
        )

    issue = db.execute(
        select(Issue).where(
            Issue.id == payload.issue_id,
            Issue.issue_type_id == payload.issue_type_id
        )
    ).scalars().first()

    if not issue:
        raise HTTPException(
            status_code=404,
            detail="Issue not found"
        )

    report = ReportIssue(
        user_id=user.id,
        issue_type_id=payload.issue_type_id,
        issue_id=payload.issue_id,
        description=payload.description,
        attachment=payload.attachment
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "message": "Issue reported successfully",
        "ticket_id": report.id
    }

@router.get("/ticket-history")
async def get_ticket_history(
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):

    user = db.execute(
        select(User).where(
            User.email == current_user_email
        )
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    tickets = db.execute(
        select(ReportIssue).where(
            ReportIssue.user_id == user.id
        )
    ).scalars().all()

    return [
        {
            "ticket_id": ticket.id,
            "issue_type": ticket.issue_type.name,
            "issue": ticket.issue.name,
            "status": ticket.status,
            "created_at": ticket.created_at
        }
        for ticket in tickets
    ]

@router.get("/ticket-details/{ticket_id}")
async def get_ticket_details(
    ticket_id: int,
    current_user_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):

    user = db.execute(
        select(User).where(
            User.email == current_user_email
        )
    ).scalars().first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    ticket = db.execute(
        select(ReportIssue).where(
            ReportIssue.id == ticket_id,
            ReportIssue.user_id == user.id
        )
    ).scalars().first()

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return {
        "ticket_id": ticket.id,
        "issue_type": ticket.issue_type.name,
        "issue": ticket.issue.name,
        "description": ticket.description,
        "attachment": ticket.attachment,
        "status": ticket.status,
        "created_at": ticket.created_at,
        "updated_at": ticket.updated_at
    }