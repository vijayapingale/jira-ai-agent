from app.services.classifier import classify_ticket
from app.services.rag_service import retrieve_context
from app.services.agent_service import run_agent
from app.services.resolution_service import generate_resolution
from app.services.jira_service import update_jira

def process_ticket(ticket: dict):
    text = ticket["summary"] + " " + ticket["description"]

    # 1. classify
    category = classify_ticket(text)

    # 2. retrieve context
    context = retrieve_context(text)

    # 3. agent execution
    actions = run_agent(text, context)

    # 4. generate resolution
    resolution = generate_resolution(context, actions)

    # 5. update jira
    update_jira(ticket["id"], resolution)