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
    # Accept header needed to get diff format for PRs
    headers["Accept"] = "application/vnd.github.v3.diff"

    response = requests.get(diff_url, headers=headers)
    if response.status_code == 200:
        return response.text
    return f"[ERROR] Diff çekilemedi: {diff_url}. HTTP Status: {response.status_code}"

def post_pr_comment(repo_full_name: str, pr_number: int, body: str) -> bool:
    """
    Posts a general comment on a Pull Request.
    """
    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    payload = {"body": body}
    
    if not GITHUB_TOKEN:
        print("[MOCK] GITHUB_TOKEN yok. PR Yorumu basılmış gibi yapıldı:\\n", body)
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
        print("[MOCK] GITHUB_TOKEN yok. Commit yorumu basılmış gibi yapıldı:\\n", body)
        return True
        
    response = requests.post(url, headers=get_headers(), json=payload)
    return response.status_code == 201
