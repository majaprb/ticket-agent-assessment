from fastapi import FastAPI, HTTPException
from datetime import datetime
from pydantic import BaseModel

app = FastAPI()

tickets = []

class TicketCreate(BaseModel):
    title: str
    description: str

class TicketUpdate(BaseModel):
    status: str
    resolution: str = ""

@app.get("/")
def root():
    return {"message": "Ticket API is running"}

next_ticket_id = 1

@app.post("/tickets")
def create_ticket(ticket_data: TicketCreate):

    global next_ticket_id

    ticket = {
        "id": next_ticket_id,
        "title": ticket_data.title,
        "description": ticket_data.description,
        "created": str(datetime.now()),
        "status": "OPEN",
        "resolution": ""
    }

    tickets.append(ticket)
    next_ticket_id += 1

    return ticket

@app.get("/tickets")
def get_tickets():
    return tickets

@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: int):

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            return ticket

    raise HTTPException(
        status_code=404,
        detail="Ticket not found"
)

@app.put("/tickets/{ticket_id}")
def update_ticket(ticket_id: int, update: TicketUpdate):

    valid_statuses = ["OPEN", "RESOLVED", "CLOSED"]

    if update.status not in valid_statuses:
        raise HTTPException(
            status_code=422,
            detail="Invalid status. Valid options: OPEN, RESOLVED, CLOSED"
        )

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            ticket["status"] = update.status

            if update.resolution is not None:
                ticket["resolution"] = update.resolution

            return ticket

    raise HTTPException(
        status_code=404,
        detail="Ticket not found"
    )

@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int):

    for ticket in tickets:
        if ticket["id"] == ticket_id:
            tickets.remove(ticket)
            return {"message": "Ticket deleted"}

    raise HTTPException(
        status_code=404,
        detail="Ticket not found"
    )