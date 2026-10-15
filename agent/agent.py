import os
import json
import requests

from openai import AzureOpenAI

API_URL = "http://127.0.0.1:8000"
TIMEOUT = 5

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")


client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION
)

# --------------------------------------------------
# LLM tool definitions
# --------------------------------------------------

TICKET_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_tickets",
            "description": "Retrieve all tickets, optionally filtered by status.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["OPEN", "RESOLVED", "CLOSED"],
                        "description": "Optional status to filter tickets."
                    }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_ticket",
            "description": "Create a new support ticket.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "Short title for the ticket."
                    },
                    "description": {
                        "type": "string",
                        "description": "Description of the problem."
                    }
                },
                "required": ["title", "description"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_ticket",
            "description": "Retrieve one ticket by its numeric ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "integer",
                        "description": "Numeric ticket ID."
                    }
                },
                "required": ["ticket_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_ticket",
            "description": "Update a ticket status and optionally its resolution.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "integer",
                        "description": "Numeric ticket ID."
                    },
                    "status": {
                        "type": "string",
                        "description": "Requested ticket status."
                    },
                    "resolution": {
                        "type": "string",
                        "description": "Optional resolution note."
                    }
                },
                "required": ["ticket_id", "status"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_ticket",
            "description": "Delete a ticket by its numeric ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "integer",
                        "description": "Numeric ticket ID."
                    }
                },
                "required": ["ticket_id"],
                "additionalProperties": False
            }
        }
    }
]
# --------------------------------------------------
# Ticket API functions
# --------------------------------------------------

def get_tickets(status=None):
    if status:
        return make_request(
            "GET",
            "/tickets",
            params={"status": status}
        )

    return make_request("GET", "/tickets")


def create_ticket(title, description):
    return make_request(
        "POST",
        "/tickets",
        json={
            "title": title,
            "description": description
        }
    )


def get_ticket(ticket_id):
    return make_request(
        "GET",
        f"/tickets/{ticket_id}"
    )


def update_ticket(ticket_id, status, resolution=""):
    return make_request(
        "PUT",
        f"/tickets/{ticket_id}",
        json={
            "status": status,
            "resolution": resolution
        }
    )


def delete_ticket(ticket_id):
    return make_request(
        "DELETE",
        f"/tickets/{ticket_id}"
    )


def handle_response(response):
    """
    Check an API response and return its JSON body.
    Raises a readable error for unsuccessful responses.
    """
    try:
        data = response.json()
    except ValueError:
        data = {"detail": response.text or "API returned a non-JSON response"}

    if response.ok:
        return data

    error_message = data.get("detail", data)
    raise RuntimeError(
        f"API error {response.status_code}: {error_message}"
    )


def make_request(method, endpoint, **kwargs):
    """
    Send a request to the API with common error handling.
    """
    url = f"{API_URL}{endpoint}"

    try:
        response = requests.request(
            method,
            url,
            timeout=TIMEOUT,
            **kwargs
        )
        return handle_response(response)

    except requests.exceptions.Timeout:
        raise RuntimeError(
            f"Request timed out after {TIMEOUT} seconds"
        )

    except requests.exceptions.ConnectionError:
        raise RuntimeError(
            f"Could not connect to the API at {API_URL}. "
            "Make sure the API server is running."
        )

    except requests.exceptions.RequestException as error:
        raise RuntimeError(
            f"Request failed: {error}"
        ) from error


def get_tickets(status=None):
    if status:
        return make_request(
            "GET",
            "/tickets",
            params={"status": status}
        )

    return make_request("GET", "/tickets")


def create_ticket(title, description):
    """Create a new ticket."""
    return make_request(
        "POST",
        "/tickets",
        json={
            "title": title,
            "description": description
        }
    )


def get_ticket(ticket_id):
    """Get a ticket by ID."""
    return make_request(
        "GET",
        f"/tickets/{ticket_id}"
    )


def update_ticket(ticket_id, status, resolution=""):
    """Update the status of a ticket."""
    return make_request(
        "PUT",
        f"/tickets/{ticket_id}",
        json={
            "status": status,
            "resolution": resolution
        }
    )


def delete_ticket(ticket_id):
    """Delete a ticket by ID."""
    return make_request(
        "DELETE",
        f"/tickets/{ticket_id}"
    )

def execute_tool(tool_name, arguments):
    """Execute the ticket tool selected by the LLM."""

    if tool_name == "get_tickets":
        return get_tickets(
            status=arguments.get("status")
        )

    elif tool_name == "create_ticket":
        return create_ticket(
            arguments["title"],
            arguments["description"]
        )

    elif tool_name == "get_ticket":
        return get_ticket(
            arguments["ticket_id"]
        )

    elif tool_name == "update_ticket":
        return update_ticket(
            arguments["ticket_id"],
            arguments["status"],
            arguments.get("resolution", "")
        )

    elif tool_name == "delete_ticket":
        return delete_ticket(
            arguments["ticket_id"]
        )

    else:
        raise ValueError(
            f"Unknown tool: {tool_name}"
        )
def run_agent(user_input):
    """Run one natural-language request through the ticket agent."""

    messages = [
        {
            "role": "system",
            "content": (
                "You are a support ticket agent. "
                "Use the available tools to create, retrieve, update, "
                "or delete tickets. "
                "If a tool returns an API business logic error, explain "
                "the error clearly and give the user actionable feedback."
            )
        },
        {
            "role": "user",
            "content": user_input
        }
    ]

    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=messages,
        tools=TICKET_TOOLS,
        tool_choice="auto",
        reasoning_effort="none"
    )

    message = response.choices[0].message

    if not message.tool_calls:
        return message.content

    messages.append(message)

    for tool_call in message.tool_calls:
        tool_name = tool_call.function.name
        arguments = json.loads(
            tool_call.function.arguments
        )

        try:
            result = execute_tool(
                tool_name,
                arguments
            )

        except RuntimeError as error:
            result = {
                "error": str(error)
            }

        messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            }
        )

    final_response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=messages,
        tools=TICKET_TOOLS,
        reasoning_effort="none"
    )

    return final_response.choices[0].message.content


if __name__ == "__main__":

    print("\n--- GenAI Ticket Agent ---")
    print("Type 'exit' to quit.")

    while True:
        user_input = input("\nYou: ")

        if user_input.lower() == "exit":
            print("\nGoodbye!")
            break

        try:
            response = run_agent(user_input)
            print(f"\nAgent: {response}")

        except Exception as error:
            print(f"\nAgent error: {error}")