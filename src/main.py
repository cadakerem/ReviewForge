from fastapi import FastAPI, Request, HTTPException, Header
from src.security import verify_signature
from src.router import route_analysis
import uvicorn

app = FastAPI(title="ReviewForge Agent", version="1.0.0")

@app.post("/webhook")
async def github_webhook(
    request: Request, 
    x_hub_signature_256: str = Header(None), 
    x_github_event: str = Header(None)
):
    body = await request.body()
    
    if not verify_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=403, detail="Invalid GitHub signature")

    payload = await request.json()

    if x_github_event == "ping":
        return {"msg": "pong"}

    if x_github_event in ["pull_request", "push"]:
        analysis_mode = route_analysis(x_github_event, payload)
        
        diff_url = ""
        repo_full_name = payload.get("repository", {}).get("full_name", "")
        pr_number = None
        commit_sha = None

        if x_github_event == "pull_request":
            diff_url = payload.get("pull_request", {}).get("diff_url", "")
            pr_number = payload.get("pull_request", {}).get("number")
        elif x_github_event == "push":
            compare_url = payload.get("compare", "")
            diff_url = compare_url + ".diff" if compare_url else ""
            commits = payload.get("commits", [])
            commit_sha = commits[-1].get("id") if commits else None

        review_result = "No diff URL provided."
        posted = False
        
        if diff_url:
            from src.github import fetch_diff, post_pr_comment, post_commit_comment
            from src.ai_reviewer import analyze_diff
            
            diff_text = fetch_diff(diff_url)
            if not diff_text.startswith("[ERROR]"):
                review_result = analyze_diff(diff_text, analysis_mode)
                
                comment_body = f"### ğŸ›¡ï¸ ReviewForge AI Analysis\n\n**Mode:** `{analysis_mode}`\n\n{review_result}"
                
                if x_github_event == "pull_request" and pr_number:
                    posted = post_pr_comment(repo_full_name, pr_number, comment_body)
                elif x_github_event == "push" and commit_sha:
                    posted = post_commit_comment(repo_full_name, commit_sha, comment_body)
            else:
                review_result = diff_text

        return {
            "status": "accepted",
            "event": x_github_event,
            "analysis_mode": analysis_mode,
            "posted_to_github": posted
        }

    return {"status": "ignored"}

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
