import os
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.github import fetch_diff, post_pr_comment, post_commit_comment
from src.ai_reviewer import analyze_diff
from src.router import route_analysis

def main():
    event_path = os.getenv("GITHUB_EVENT_PATH")
    event_name = os.getenv("GITHUB_EVENT_NAME")
    
    if not event_path or not os.path.exists(event_path):
        print("GitHub event path not found. Exiting.")
        sys.exit(1)

    with open(event_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    repo_full_name = payload.get("repository", {}).get("full_name")
    
    diff_url = ""
    pr_number = None
    commit_sha = None

    if event_name == "pull_request":
        diff_url = payload.get("pull_request", {}).get("diff_url", "")
        pr_number = payload.get("pull_request", {}).get("number")
    elif event_name == "push":
        compare_url = payload.get("compare", "")
        diff_url = compare_url + ".diff" if compare_url else ""
        commits = payload.get("commits", [])
        commit_sha = commits[-1].get("id") if commits else None
    else:
        print(f"Unsupported event: {event_name}")
        sys.exit(0)

    if not diff_url:
        print("No diff URL found in payload.")
        sys.exit(0)

    print(f"Fetching diff from {diff_url}...")
    diff_text = fetch_diff(diff_url)
    
    if diff_text.startswith("[ERROR]"):
        print(diff_text)
        sys.exit(1)

    if not diff_text.strip():
        print("Diff is empty. Nothing to review.")
        sys.exit(0)

    analysis_mode = route_analysis(event_name, payload)
    print(f"Routing to: {analysis_mode}")
    
    review_result = analyze_diff(diff_text, analysis_mode)
    
    comment_body = f"### 🛡️ ReviewForge AI Analysis\\n\\n**Mode:** `{analysis_mode}`\\n\\n{review_result}"
    
    if event_name == "pull_request" and pr_number:
        post_pr_comment(repo_full_name, pr_number, comment_body)
        print("Comment posted to PR.")
    elif event_name == "push" and commit_sha:
        post_commit_comment(repo_full_name, commit_sha, comment_body)
        print("Comment posted to Commit.")
    
if __name__ == "__main__":
    main()
