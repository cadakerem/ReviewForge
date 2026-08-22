import os
from openai import OpenAI

# Initialize the OpenAI client pointing to Nvidia NIM
# User needs to set NVIDIA_API_KEY in their environment
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

def analyze_diff(diff_text: str, mode: str) -> str:
    """
    Analyzes a git diff using Nvidia NIM models based on the routing mode.
    mode: "LIGHT_ANALYSIS" or "DEEP_ANALYSIS"
    """
    if not NVIDIA_API_KEY:
        return "[MOCK REVIEW] NVIDIA_API_KEY ayarlanmadığı için analiz simüle edildi. Kod temiz görünüyor!"

    if mode == "DEEP_ANALYSIS":
        model_name = "nvidia/nemotron-3-ultra-550b-a55b"
        system_prompt = "Sen kıdemli bir Security Engineer ve Software Architect'sin. Aşağıdaki kod diff'ini kritik güvenlik zafiyetleri, mimari hatalar ve performans sorunları için derinlemesine incele."
    else:
        model_name = "meta/llama-3.3-70b-instruct"
        system_prompt = "Sen hızlı ve pratik bir Code Reviewer'sın. Bu diff'i bariz bug'lar, typo'lar ve basit stil hataları için incele. Çok kısa ve net ol."

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Lütfen şu diff'i incele:\n\n```diff\n{diff_text}\n```"}
            ],
            temperature=0.2,
            top_p=0.7,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"[ERROR] AI analiz hatası: {str(e)}"
