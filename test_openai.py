import os
from openai import OpenAI

client = OpenAI(
    api_key="DUMMY",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

try:
    completion = client.chat.completions.create(
        model="gemini-1.5-flash",
        messages=[{"role": "user", "content": "hi"}]
    )
except Exception as e:
    print(str(e))
