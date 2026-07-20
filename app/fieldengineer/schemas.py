from pydantic import BaseModel
from typing import Optional


class ReportIssueCreateSchema(BaseModel):
    issue_type_id: int
    issue_id: int
    description: Optional[str] = None
    attachment: Optional[str] = None