import os
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

def fetch_diff(diff_url: str) -> str:
    """
    Fetches the raw diff text from a GitHub diff URL.
    """
    headers = {}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    
    # Accept header needed to get diff format for PRs
    headers["Accept"] = "application/vnd.github.v3.diff"

    response = requests.get(diff_url, headers=headers)
    if response.status_code == 200:
        return response.text
    return f"[ERROR] Diff çekilemedi: {diff_url}. HTTP Status: {response.status_code}"
