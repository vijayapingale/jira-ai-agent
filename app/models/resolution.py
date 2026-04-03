"""
Resolution-related Pydantic models
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ResolutionStep(BaseModel):
    """Individual resolution step"""
    action: str
    description: str
    tool_used: Optional[str] = None
    result: Optional[str] = None
    status: str = "pending"  # pending, in_progress, completed, failed


class Resolution(BaseModel):
    """Ticket resolution plan and execution"""
    ticket_id: str
    classification: str
    steps: List[ResolutionStep] = Field(default_factory=list)
    status: str = "planned"  # planned, in_progress, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    final_summary: Optional[str] = None


class ResolutionResult(BaseModel):
    """Final resolution result"""
    success: bool
    message: str
    resolution_id: str
    execution_time_seconds: Optional[float] = None
