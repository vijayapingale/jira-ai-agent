"""
LLM-based ticket classification service
"""

from typing import Dict, Any
from app.models.ticket import TicketClassification
from app.core.config import settings

from app.core.bedrock import invoke_llm


class TicketClassifier:
    """Service for classifying Jira tickets using LLM"""
    
    def __init__(self):
        self.model_name = settings.model_name
    
    async def classify_ticket(self, ticket_data: Dict[str, Any]) -> TicketClassification:
        """Classify a ticket based on its content"""
        
        # TODO: Implement LLM classification logic
        # This would involve:
        # 1. Formatting the ticket data for the LLM
        # 2. Making API call to OpenAI/other LLM
        # 3. Parsing the response into structured classification
        
        return TicketClassification(
            ticket_id=ticket_data.get("id", ""),
            category="bug",
            severity="medium",
            urgency="normal",
            confidence=0.85,
            reasoning="Sample classification - implement LLM logic"
        )



def classify_ticket(text):
    prompt = f"Classify this ticket: {text}"
    return invoke_llm(prompt)