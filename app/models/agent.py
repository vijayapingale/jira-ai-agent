"""
Agent-related Pydantic models
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class AgentTool(BaseModel):
    """Agent tool definition"""
    name: str
    description: str
    parameters: Dict[str, Any] = Field(default_factory=dict)
    enabled: bool = True


class AgentExecution(BaseModel):
    """Agent execution record"""
    execution_id: str
    ticket_id: str
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    responses: List[Dict[str, Any]] = Field(default_factory=list)
    status: str = "running"  # running, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class AgentConfig(BaseModel):
    """Agent configuration"""
    model_name: str = "gpt-4"
    temperature: float = 0.1
    max_tokens: int = 2000
    tools: List[AgentTool] = Field(default_factory=list)
    system_prompt: Optional[str] = None
