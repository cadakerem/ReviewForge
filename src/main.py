from fastapi import FastAPI, Request, HTTPException, Header, BackgroundTasks
from src.security import verify_signature
from src.core import process_webhook_event
import uvicorn

app = FastAPI(title='ReviewForge Agent', version='1.0.0')

def background_process_event(event_name, payload):
    process_webhook_event(event_name, payload)

@app.post('/webhook')
async def github_webhook(
    request: Request, 
    background_tasks: BackgroundTasks,
    x_hub_signature_256: str = Header(None), 
    x_github_event: str = Header(None)
):
    body = await request.body()
    
    if not verify_signature(body, x_hub_signature_256):
        raise HTTPException(status_code=403, detail='Invalid GitHub signature')

    payload = await request.json()

    if x_github_event == 'ping':
        return {'msg': 'pong'}

    if x_github_event in ['pull_request', 'push']:
        background_tasks.add_task(background_process_event, x_github_event, payload)
        return {
            'status': 'accepted',
            'event': x_github_event,
            'message': 'Review dispatched to background task'
        }

    return {'status': 'ignored'}

if __name__ == '__main__':
    uvicorn.run('src.main:app', host='0.0.0.0', port=8000, reload=True)

