from fastapi import APIRouter, Request
from app.workers.ticket_worker import process_ticket

router = APIRouter()

@router.post("/webhook")
async def jira_webhook(req: Request):
    payload = await req.json()

    ticket = {
        "id": payload["issue"]["key"],
        "summary": payload["issue"]["fields"]["summary"],
        "description": payload["issue"]["fields"]["description"]
    }

    process_ticket(ticket)  # direct call for now (no SQS yet)

    return {"status": "processed"}