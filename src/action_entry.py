import os
import json
import sys
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.github import fetch_diff, post_pr_comment, post_commit_comment
from src.ai_reviewer import analyze_diff
from src.router import route_analysis

# Fix #2: Only trusted contributors trigger AI analysis to prevent prompt injection and cost-based DoS
TRUSTED_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR"}

def main():
    event_path = os.getenv("GITHUB_EVENT_PATH")
    event_name = os.getenv("GITHUB_EVENT_NAME")

    if not event_path or not os.path.exists(event_path):
        print("GitHub event path not found. Exiting.")
        sys.exit(1)

    with open(event_path, "r", encoding="utf-8") as f:
        payload = json.load(f)

    # Fix #2: Check author association before doing anything
    if event_name == "pull_request":
        association = payload.get("pull_request", {}).get("author_association", "NONE")
        if association not in TRUSTED_ASSOCIATIONS:
            print(f"[Security] PR author association is '{association}'. Skipping analysis for untrusted contributor.")
            sys.exit(0)

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

    # DIFF TRUNCATION (Anti-DoS / Cost Protection)
    MAX_DIFF_LENGTH = 20000 # Approx 5000-7000 tokens
    if len(diff_text) > MAX_DIFF_LENGTH:
        print(f"[Warning] Diff is too large ({len(diff_text)} chars). Truncating to {MAX_DIFF_LENGTH} chars to prevent token exhaustion.")
        diff_text = diff_text[:MAX_DIFF_LENGTH] + "\n\n... [DIFF TRUNCATED TO PREVENT TOKEN EXHAUSTION] ..."

    # Load optional custom rules
    custom_rules = ""
    rules_path = os.path.join(os.getenv("GITHUB_WORKSPACE", "."), ".reviewforge.md")
    if os.path.exists(rules_path):
        with open(rules_path, "r", encoding="utf-8") as f:
            custom_rules = f.read()
            print("Custom rules loaded from .reviewforge.md")

    analysis_mode = route_analysis(event_name, payload)
    print(f"Routing to: {analysis_mode}")

    review_result = analyze_diff(diff_text, analysis_mode, custom_rules)

    # Fix #4: Robust JSON parsing — always clean the JSON block even if parsing fails
    json_match = re.search(
        r'```json\s*(\{[^`]*?"create_issue"\s*:\s*true[^`]*?\})\s*```',
        review_result,
        re.DOTALL
    )

    issue_url = None
    # Always strip the raw JSON block from review body regardless of parse outcome
    final_review_body = review_result.replace(json_match.group(0), "").strip() if json_match else review_result

    if json_match:
        try:
            issue_data = json.loads(json_match.group(1))
            issue_title = issue_data.get("title", "Critical Vulnerability Detected")
            labels = issue_data.get("labels", ["bug", "security"])

            # Add traceability note
            context_note = "\n\n---\n"
            if event_name == "pull_request" and pr_number:
                context_note += f"🔍 *Detected by ReviewForge AI during review of [PR #{pr_number}].*"
            elif event_name == "push" and commit_sha:
                context_note += f"🔍 *Detected by ReviewForge AI during review of commit `{commit_sha[:7]}`.*"

            issue_body = final_review_body + context_note

            from src.github import create_github_issue
            issue_resp = create_github_issue(repo_full_name, issue_title, issue_body, labels)
            if issue_resp:
                issue_url = issue_resp.get("html_url")
                print(f"Critical issue found! Labeled GitHub Issue created: {issue_url}")

            if issue_url:
                final_review_body += f"\n\n🚨 **CRITICAL:** A critical problem was detected in this PR. An issue was automatically created: [View Issue]({issue_url})."

        except Exception as e:
            print(f"[Warning] JSON parse failed: {e}. Raw JSON block was cleaned from output.")

    comment_body = f"### 🛡️ ReviewForge AI Analysis\n\n**Mode:** `{analysis_mode}`\n\n{final_review_body}"

    if event_name == "pull_request" and pr_number:
        post_pr_comment(repo_full_name, pr_number, comment_body)
        print("Comment posted to PR.")
    elif event_name == "push" and commit_sha:
        post_commit_comment(repo_full_name, commit_sha, comment_body)
        print("Comment posted to Commit.")


if __name__ == "__main__":
    main()
