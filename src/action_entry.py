import os
import json
import sys
import re

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

    # Check for custom rules
    custom_rules = ""
    rules_path = os.path.join(os.getenv("GITHUB_WORKSPACE", "."), ".reviewforge.md")
    if os.path.exists(rules_path):
        with open(rules_path, "r", encoding="utf-8") as f:
            custom_rules = f.read()
            print("Custom rules loaded from .reviewforge.md")

    analysis_mode = route_analysis(event_name, payload)
    print(f"Routing to: {analysis_mode}")
    
    review_result = analyze_diff(diff_text, analysis_mode, custom_rules)
    
    # Check for issue creation JSON
    json_match = re.search(r'```json\s*(\{.*?"create_issue":\s*true.*?\})\s*```', review_result, re.DOTALL)
    
    issue_url = None
    final_review_body = review_result
    
    if json_match:
        try:
            issue_data = json.loads(json_match.group(1))
            issue_title = issue_data.get("title", "Critical Vulnerability Detected")
            labels = issue_data.get("labels", ["bug", "security"])
            
            # Add context trace
            context_note = "\n\n---\n"
            if event_name == "pull_request" and pr_number:
                context_note += f"ğŸ” *Bu sorun, ReviewForge AI tarafÄ±ndan [PR #{pr_number}] numaralÄ± kod incelemesi sÄ±rasÄ±nda otomatik olarak tespit edilmiÅŸtir.*"
            elif event_name == "push" and commit_sha:
                context_note += f"ğŸ” *Bu sorun, ReviewForge AI tarafÄ±ndan `{commit_sha[:7]}` numaralÄ± commit incelemesi sÄ±rasÄ±nda otomatik olarak tespit edilmiÅŸtir.*"
            
            # Clean JSON from the issue body
            issue_body = review_result.replace(json_match.group(0), "").strip() + context_note
            
            from src.github import create_github_issue
            issue_resp = create_github_issue(repo_full_name, issue_title, issue_body, labels)
            if issue_resp:
                issue_url = issue_resp.get("html_url")
                print(f"ğŸš¨ Kritik hata bulundu, Etiketli Issue AÃ§Ä±ldÄ±! URL: {issue_url}")
                
            # Clean JSON from the PR comment and add a note
            final_review_body = review_result.replace(json_match.group(0), "").strip()
            if issue_url:
                final_review_body += f"\n\nğŸš¨ **DÄ°KKAT:** Bu PR'da kritik bir sorun tespit ettim ve detaylarÄ± iÃ§in otomatik olarak [ÅŸu Issue'yu aÃ§tÄ±m]({issue_url})."
                
        except Exception as e:
            print(f"JSON Parse hatasÄ±: {e}")

    comment_body = f"### ğŸ›¡ï¸ ReviewForge AI Analysis\n\n**Mode:** `{analysis_mode}`\n\n{final_review_body}"
    
    if event_name == "pull_request" and pr_number:
        post_pr_comment(repo_full_name, pr_number, comment_body)
        print("Comment posted to PR.")
    elif event_name == "push" and commit_sha:
        post_commit_comment(repo_full_name, commit_sha, comment_body)
        print("Comment posted to Commit.")

    
if __name__ == "__main__":
    main()
