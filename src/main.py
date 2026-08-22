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
        
        # URL for diff
        diff_url = ""
        if x_github_event == "pull_request":
            diff_url = payload.get("pull_request", {}).get("diff_url", "")
        elif x_github_event == "push":
            diff_url = payload.get("compare", "") + ".diff"

        review_result = "No diff URL provided."
        if diff_url:
            from src.github import fetch_diff
            from src.ai_reviewer import analyze_diff
            
            diff_text = fetch_diff(diff_url)
            if not diff_text.startswith("[ERROR]"):
                review_result = analyze_diff(diff_text, analysis_mode)
            else:
                review_result = diff_text

        return {
            "status": "accepted",
            "event": x_github_event,
            "analysis_mode": analysis_mode,
            "review": review_result
        }

    return {"status": "ignored"}

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
