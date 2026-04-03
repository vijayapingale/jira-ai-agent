"""
Prompt templates for LLM interactions
"""

from typing import Dict, Any


class PromptTemplates:
    """Collection of prompt templates for various LLM interactions"""
    
    TICKET_CLASSIFICATION_PROMPT = """
You are an expert at analyzing Jira tickets and classifying them for automated resolution.

Analyze the following Jira ticket and classify it into one of these categories:
- bug: Software defects, errors, unexpected behavior
- incident: Service outages, performance issues, urgent problems
- feature_request: New functionality requests
- documentation: Documentation updates or improvements
- question: User questions or clarifications
- other: Anything that doesn't fit the above categories

Also assess:
- severity: low, medium, high, critical
- urgency: low, normal, high, urgent

Ticket Details:
Title: {title}
Description: {description}
Priority: {priority}
Labels: {labels}
Components: {components}

Provide your response in JSON format:
{{
    "category": "category_name",
    "severity": "severity_level", 
    "urgency": "urgency_level",
    "confidence": 0.95,
    "reasoning": "Brief explanation of your classification"
}}
"""
    
    RESOLUTION_PLANNING_PROMPT = """
You are an expert DevOps engineer who specializes in troubleshooting and resolving technical issues.

Based on the ticket classification and content, create a step-by-step resolution plan.

Ticket Information:
- ID: {ticket_id}
- Category: {category}
- Severity: {severity}
- Title: {title}
- Description: {description}

Available Tools:
- logs_tool: Access and analyze application logs
- db_tool: Perform database operations and health checks  
- restart_service_tool: Restart application services
- jira_tool: Update Jira tickets and add comments

Create a resolution plan with specific steps. For each step, specify:
1. The action to take
2. Which tool to use
3. What to look for or verify

Respond in JSON format:
{{
    "steps": [
        {{
            "action": "analyze_logs",
            "description": "Check application logs for errors related to the issue",
            "tool_used": "logs_tool",
            "parameters": {{"service": "api-service", "time_range": "1h"}}
        }}
    ]
}}
"""
    
    AGENT_SYSTEM_PROMPT = """
You are an AI assistant specialized in resolving Jira tickets automatically. You have access to various tools to investigate and fix issues.

Your capabilities include:
- Analyzing application logs to identify root causes
- Checking database connectivity and performance
- Restarting services when needed
- Updating Jira tickets with progress

When working on a ticket:
1. Always analyze the issue thoroughly before taking action
2. Use the most appropriate tool for each investigation step
3. Document your findings and actions clearly
4. Only restart services if it's necessary and safe
5. Update the Jira ticket with your progress and final resolution

Be methodical, safety-conscious, and provide clear explanations for your actions.
"""
    
    RAG_QUERY_ENHANCEMENT_PROMPT = """
You are helping to enhance a search query for retrieving relevant technical documentation.

Original Query: {query}
Context: This is for resolving a Jira ticket about: {ticket_context}

Enhance the query to be more specific and likely to find relevant technical documentation. Consider:
- Technical terms and keywords
- Common error patterns
- Related systems or components
- Troubleshooting steps

Enhanced Query: [Your enhanced query here]
"""
    
    SUMMARIZATION_PROMPT = """
Summarize the following resolution process for a Jira ticket:

Ticket: {ticket_id}
Category: {category}
Steps Taken: {steps}
Results: {results}
Total Time: {execution_time} seconds

Create a concise summary suitable for:
1. Adding as a comment to the Jira ticket
2. Documentation purposes
3. Future reference for similar issues

Include:
- What was identified as the root cause
- What actions were taken
- The final resolution
- Any lessons learned

Summary:
"""
    
    @staticmethod
    def format_classification_prompt(ticket_data: Dict[str, Any]) -> str:
        """Format the classification prompt with ticket data"""
        
        return PromptTemplates.TICKET_CLASSIFICATION_PROMPT.format(
            title=ticket_data.get("summary", ""),
            description=ticket_data.get("description", ""),
            priority=ticket_data.get("priority", ""),
            labels=", ".join(ticket_data.get("labels", [])),
            components=", ".join(ticket_data.get("components", []))
        )
    
    @staticmethod
    def format_resolution_planning_prompt(ticket_data: Dict[str, Any], classification: Dict[str, Any]) -> str:
        """Format the resolution planning prompt"""
        
        return PromptTemplates.RESOLUTION_PLANNING_PROMPT.format(
            ticket_id=ticket_data.get("id", ""),
            category=classification.get("category", ""),
            severity=classification.get("severity", ""),
            title=ticket_data.get("summary", ""),
            description=ticket_data.get("description", "")
        )
    
    @staticmethod
    def format_summarization_prompt(resolution_data: Dict[str, Any]) -> str:
        """Format the summarization prompt"""
        
        return PromptTemplates.SUMMARIZATION_PROMPT.format(
            ticket_id=resolution_data.get("ticket_id", ""),
            category=resolution_data.get("category", ""),
            steps=resolution_data.get("steps", []),
            results=resolution_data.get("results", ""),
            execution_time=resolution_data.get("execution_time", 0)
        )
