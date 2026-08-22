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
        return {
            "status": "accepted",
            "event": x_github_event,
            "analysis_mode": analysis_mode
        }

    return {"status": "ignored"}

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
