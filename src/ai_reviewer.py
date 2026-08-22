import os
from openai import OpenAI

# Multi-Provider Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "nvidia").lower()  # openai, nvidia, groq, custom
AI_API_KEY = os.getenv("AI_API_KEY", "")
AI_BASE_URL = os.getenv("AI_BASE_URL", None)

# Dynamic Model Configuration
LIGHT_MODEL = os.getenv("LIGHT_MODEL", "meta/llama-3.3-70b-instruct")
DEEP_MODEL = os.getenv("DEEP_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")

def get_client():
    if not AI_API_KEY:
        return None
        
    # Auto-configure base URL for known providers if not explicitly set
    base_url = AI_BASE_URL
    if not base_url:
        if AI_PROVIDER == "nvidia":
            base_url = "https://integrate.api.nvidia.com/v1"
        elif AI_PROVIDER == "groq":
            base_url = "https://api.groq.com/openai/v1"
        elif AI_PROVIDER == "openai":
            base_url = "https://api.openai.com/v1"
        elif AI_PROVIDER == "gemini":
            # Google's official OpenAI-compatible endpoint
            base_url = "https://generativelanguage.googleapis.com/v1beta/openai/"

    return OpenAI(base_url=base_url, api_key=AI_API_KEY)

def analyze_diff(diff_text: str, mode: str) -> str:
    """
    Analyzes a git diff using configured AI providers.
    Supports dynamic models to prevent deprecation breaks.
    """
    client = get_client()
    if not client:
        return f"[MOCK REVIEW] AI_API_KEY ayarlanmadığı için analiz simüle edildi. ({mode})"

    model_name = DEEP_MODEL if mode == "DEEP_ANALYSIS" else LIGHT_MODEL
    
    if mode == "DEEP_ANALYSIS":
        system_prompt = (
            "Sen kıdemli bir Security Engineer ve Software Architect'sin. Aşağıdaki kod diff'ini kritik güvenlik zafiyetleri, mimari hatalar ve performans sorunları için derinlemesine incele.\n\n"
            "ÖNEMLİ KURAL: Eğer kodda projenin çökmesine veya hacklenmesine yol açacak KESİN ve KRİTİK bir hata bulursan, "
            "cevabının en sonuna MUTLAKA şu formatta bir JSON bloğu ekle:\n"
            "```json\n"
            '{"create_issue": true, "title": "Sorunun Kısa Başlığı", "labels": ["bug", "security"]}\n'
            "```\n"
            "Etiketleri (labels) sorunun türüne göre ('bug', 'security', 'performance', 'architecture') mantıklı şekilde seçebilirsin."
        )
    else:
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
        return f"[ERROR] AI analiz hatası ({model_name}): {str(e)}"
