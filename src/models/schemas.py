from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Any

class Issue(BaseModel):
    number: int
    html_url: str
    state: Literal["open", "closed"]
    title: str
    body: Optional[str] = None
    labels: List[str] = []
    created_at: str
    updated_at: str

class CreateIssueRequest(BaseModel):
    title: str = Field(min_length=1)
    body: Optional[str] = None
    labels: Optional[List[str]] = None

class UpdateIssueRequest(BaseModel):
    title: Optional[str] = None
    body: Optional[str] = None
    state: Optional[str] = None

class CreateCommentRequest(BaseModel):
    body: str = Field(min_length=1)

class Comment(BaseModel):
    id: int
    body: str
    user: Any
    created_at: str
    html_url: str

class ErrorResponse(BaseModel):
    error: str
    details: Optional[Any] = None
    request_id: Optional[str] = None

class Event(BaseModel):
    id: str
    event: Literal["issues","issue_comment","ping"]
    action: Optional[str] = None
    issue_number: Optional[int] = None
    timestamp: str
