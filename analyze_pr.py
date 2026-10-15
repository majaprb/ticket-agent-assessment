import os
import requests

from openai import AzureOpenAI

AZURE_OPENAI_ENDPOINT = os.getenv(
    "AZURE_OPENAI_ENDPOINT", ""
).strip()

AZURE_OPENAI_API_KEY = os.getenv(
    "AZURE_OPENAI_API_KEY", ""
).strip()

AZURE_OPENAI_DEPLOYMENT = os.getenv(
    "AZURE_OPENAI_DEPLOYMENT", ""
).strip()

AZURE_OPENAI_API_VERSION = os.getenv(
    "AZURE_OPENAI_API_VERSION", ""
).strip()


client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=AZURE_OPENAI_API_VERSION
)

def analyze_diff(diff):
    """Send a pull request diff to Azure OpenAI for review."""

    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a code review assistant. "
                    "Review the pull request diff. "
                    "Provide a short summary of the changes and "
                    "suggest any important improvements."
                )
            },
            {
                "role": "user",
                "content": f"Review this pull request diff:\n\n{diff}"
            }
        ],
        reasoning_effort="none"
    )

    return response.choices[0].message.content

def get_pr_diff():
    """Download the pull request diff from GitHub."""

    repository = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")
    github_token = os.getenv("GITHUB_TOKEN")

    if not repository:
        raise RuntimeError("GITHUB_REPOSITORY is not set.")

    if not pr_number:
        raise RuntimeError("PR_NUMBER is not set.")

    if not github_token:
        raise RuntimeError("GITHUB_TOKEN is not set.")

    url = (
        f"https://api.github.com/repos/"
        f"{repository}/pulls/{pr_number}"
    )

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github.v3.diff"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    return response.text

def post_pr_comment(review):
    """Post the LLM review as a comment on the pull request."""

    repository = os.getenv("GITHUB_REPOSITORY")
    pr_number = os.getenv("PR_NUMBER")
    github_token = os.getenv("GITHUB_TOKEN")

    if not repository:
        raise RuntimeError("GITHUB_REPOSITORY is not set.")

    if not pr_number:
        raise RuntimeError("PR_NUMBER is not set.")

    if not github_token:
        raise RuntimeError("GITHUB_TOKEN is not set.")

    url = (
        f"https://api.github.com/repos/"
        f"{repository}/issues/{pr_number}/comments"
    )

    headers = {
        "Authorization": f"Bearer {github_token}",
        "Accept": "application/vnd.github+json"
    }

    response = requests.post(
        url,
        headers=headers,
        json={"body": review},
        timeout=30
    )

    response.raise_for_status()

    return response.json()

def main():
    print("Getting pull request diff...")
    diff = get_pr_diff()

    print("Sending diff to Azure OpenAI...")
    review = analyze_diff(diff)

    print("Posting review to pull request...")
    post_pr_comment(review)

    print("PR review posted successfully.")


if __name__ == "__main__":
    main()
