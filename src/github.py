import os
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

def get_headers():
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    return headers

def fetch_diff(diff_url: str) -> str:
    """
    Fetches the raw diff text from a GitHub diff URL.
    """
    headers = get_headers()
    headers["Accept"] = "application/vnd.github.v3.diff"

    response = requests.get(diff_url, headers=headers)
    if response.status_code == 200:
        return response.text
    return f"[ERROR] Could not fetch diff: {diff_url}. HTTP Status: {response.status_code}"

def fetch_pr_files(repo_full_name: str, pr_number: int) -> list:
    """
    Fix #5: Fetches the list of changed file paths for a Pull Request
    via the GitHub API, since file paths are not included in the webhook payload.
    Returns a list of filename strings.
    """
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/files"
    response = requests.get(url, headers=get_headers(), params={"per_page": 100})
    if response.status_code == 200:
        return [f["filename"] for f in response.json()]
    print(f"[Warning] Could not fetch PR files: HTTP {response.status_code}")
    return []

def post_pr_comment(repo_full_name: str, pr_number: int, body: str) -> bool:
    """
    Posts a general comment on a Pull Request.
    """
    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    payload = {"body": body}

    if not GITHUB_TOKEN:
        print("[MOCK] No GITHUB_TOKEN. Simulating PR comment:\n", body)
        return True

    response = requests.post(url, headers=get_headers(), json=payload)
    return response.status_code == 201

def post_commit_comment(repo_full_name: str, commit_sha: str, body: str) -> bool:
    """
    Posts a comment on a specific Commit (Push events).
    """
    url = f"https://api.github.com/repos/{repo_full_name}/commits/{commit_sha}/comments"
    payload = {"body": body}

    if not GITHUB_TOKEN:
        print("[MOCK] No GITHUB_TOKEN. Simulating commit comment:\n", body)
        return True

    response = requests.post(url, headers=get_headers(), json=payload)
    return response.status_code == 201

def create_github_issue(repo_full_name: str, title: str, body: str, labels: list) -> dict:
    """
    Creates a labeled GitHub Issue for critical findings.
    """
    url = f"https://api.github.com/repos/{repo_full_name}/issues"
    payload = {
        "title": f"🚨 [ReviewForge] {title}",
        "body": body,
        "labels": labels
    }

    if not GITHUB_TOKEN:
        print(f"[MOCK] No GITHUB_TOKEN. Simulating issue creation: {title}")
        return {"html_url": "https://github.com/mock/issue/1", "number": 1}

    response = requests.post(url, headers=get_headers(), json=payload)
    if response.status_code == 201:
        return response.json()
    print(f"[ERROR] Issue creation failed: {response.status_code} - {response.text}")
    return {}
