"""
Ticket-related Pydantic models
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class JiraTicket(BaseModel):
    """Jira ticket model"""
    id: str
    key: str
    summary: str
    description: Optional[str] = None
    status: str
    priority: Optional[str] = None
    assignee: Optional[str] = None
    reporter: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    labels: List[str] = Field(default_factory=list)
    components: List[str] = Field(default_factory=list)


class TicketClassification(BaseModel):
    """Ticket classification result"""
    ticket_id: str
    category: str
    severity: str
    urgency: str
    confidence: float
    reasoning: str
