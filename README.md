# Ticket Agent Assessment

This project is a small support ticket system built as part of the technical assessment.

It contains four main parts:

- A FastAPI ticket API
- A GenAI agent using Azure OpenAI
- An automated PR review workflow using GitHub Actions
- A small Terraform setup for Azure

## Project structure

```text
.github/workflows/pr-review.yml   GitHub Actions PR review workflow
agent/agent.py                    GenAI ticket agent
infra/                            Terraform files
analyze_pr.py                     PR review script
main.py                           FastAPI ticket API
requirements.txt                  Python dependencies
```

## Setup

Install the dependencies:

```bash
pip install -r requirements.txt
```

The project uses the following Azure OpenAI environment variables:

```text
AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_API_KEY
AZURE_OPENAI_DEPLOYMENT
AZURE_OPENAI_API_VERSION
```

I kept these outside the source code so credentials are not committed to Git.

For PowerShell, they can be set like this:

```powershell
$env:AZURE_OPENAI_ENDPOINT="your-endpoint"
$env:AZURE_OPENAI_API_KEY="your-key"
$env:AZURE_OPENAI_DEPLOYMENT="your-deployment"
$env:AZURE_OPENAI_API_VERSION="your-api-version"
```

## Ticket API

The API is in `main.py` and uses FastAPI.

Start it with:

```bash
uvicorn main:app --reload
```

It runs locally at `http://127.0.0.1:8000`.

The API supports creating, retrieving, updating and deleting tickets, as well as filtering tickets by status.

The supported statuses are:

- `OPEN`
- `RESOLVED`
- `CLOSED`

The API also handles invalid statuses with a 422 response and missing tickets with a 404 response.

Tickets are stored in memory for this assessment, so ticket data is reset when the API is restarted.

## GenAI agent

The agent is in `agent/agent.py`.

With the API running in one terminal, start the agent in another:

```bash
python agent/agent.py
```

The agent takes natural language requests rather than requiring the user to choose an API operation manually.

Examples:

```text
Create a new ticket about a keyboard not working.

Retrieve all open tickets.

Get details for ticket 1.

Update ticket 1 to have the status PROGRESS.

Update ticket 1 to be RESOLVED, adding "Replaced faulty cable" as the resolution.

Update ticket 9999 to CLOSED.
```

Azure OpenAI decides which ticket function to call and passes the arguments to the API.

I left status validation in the API rather than relying on the LLM. For example, if the user asks for `PROGRESS`, the request reaches the API, the API rejects the invalid status, and the agent explains that the valid options are `OPEN`, `RESOLVED`, and `CLOSED`.

The same approach is used for missing tickets. The API returns a 404 and the agent turns that into a more useful message for the user.

## PR review bot

`analyze_pr.py` contains the PR review logic.

The GitHub Actions workflow is:

```text
.github/workflows/pr-review.yml
```

It runs when a pull request is opened or updated.

The workflow:

1. Gets the PR diff from GitHub.
2. Sends the diff to Azure OpenAI.
3. Asks for a short summary and review suggestions.
4. Posts the result back to the PR as one comment.

The Azure configuration is stored as GitHub Actions repository secrets:

```text
AZURE_OPENAI_ENDPOINT
AZURE_OPENAI_API_KEY
AZURE_OPENAI_DEPLOYMENT
AZURE_OPENAI_API_VERSION
```

`GITHUB_TOKEN` is supplied by GitHub Actions.

I tested the workflow with a real pull request and confirmed that the workflow ran successfully and posted the generated review as a PR comment.

## Terraform

The Terraform files are under `infra/`:

```text
infra/
├── main.tf
├── variables.tf
└── outputs.tf
```

The configuration contains a simple Azure infrastructure skeleton with:

- Resource Group
- Linux App Service Plan
- Linux Web App

To check it:

```bash
cd infra
terraform init
terraform validate
```

The configuration was validated successfully.

I did not run `terraform apply`, since deploying the infrastructure was not necessary for the local implementation.

## Security

Secrets are not hard-coded in the Python files.

Locally, Azure credentials are read from environment variables. In GitHub Actions, the same values are stored using repository secrets.

The `.gitignore` also excludes local files such as:

```text
venv/
__pycache__/
.env
.terraform/
*.tfstate
```

## Running everything locally

Start the API:

```bash
uvicorn main:app --reload
```

Then, in a second terminal with the Azure environment variables configured:

```bash
python agent/agent.py
```

The agent can then be used through the command line with natural-language ticket requests.

## If this were production

One thing I would change for a production system is the ticket storage.

For this assessment, tickets are stored in memory to keep the API simple. This means the data is lost whenever the API restarts.

In production, I would move ticket storage to a persistent database and keep the API layer stateless. This would prevent ticket data from being lost when the API process restarts and make the service more suitable for running across multiple instances.
