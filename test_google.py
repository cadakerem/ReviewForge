import urllib.request
import json
req = urllib.request.Request(
    'https://generativelanguage.googleapis.com/v1beta/openai/chat/completions',
    method='POST',
    headers={'Authorization': 'Bearer DUMMY', 'Content-Type': 'application/json'},
    data=json.dumps({"model":"gemini-1.5-flash", "messages":[{"role":"user","content":"hi"}]}).encode('utf-8')
)
try:
    urllib.request.urlopen(req)
except Exception as e:
    print(e.read().decode())
