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

def analyze_diff(diff_text: str, mode: str, custom_rules: str = "") -> str:
    """
    Analyzes a git diff using configured AI providers.
    Supports dynamic models to prevent deprecation breaks.
    """
    client = get_client()
    if not client:
        return f"[MOCK REVIEW] AI_API_KEY ayarlanmadÄ±ÄŸÄ± iÃ§in analiz simÃ¼le edildi. ({mode})"

    model_name = DEEP_MODEL if mode == "DEEP_ANALYSIS" else LIGHT_MODEL
    
    if mode == "DEEP_ANALYSIS":
        system_prompt = (
            "Sen kÄ±demli bir Security Engineer ve Software Architect'sin. AÅŸaÄŸÄ±daki kod diff'ini kritik gÃ¼venlik zafiyetleri, mimari hatalar ve performans sorunlarÄ± iÃ§in derinlemesine incele.\n\n"
            "Ã–NEMLÄ° KURAL: Sadece sorunu sÃ¶yleyip bÄ±rakma. GeliÅŸtiricinin kopyalayÄ±p yapÄ±ÅŸtÄ±rarak sorunu anÄ±nda Ã§Ã¶zebileceÄŸi DÃœZELTÄ°LMÄ°Å KOD bloÄŸunu da mutlaka ver.\n\n"
            "ISSUE KURALI: EÄŸer kodda projenin Ã§Ã¶kmesine veya hacklenmesine yol aÃ§acak KESÄ°N ve KRÄ°TÄ°K bir hata bulursan, "
            "cevabÄ±nÄ±n en sonuna MUTLAKA ÅŸu formatta bir JSON bloÄŸu ekle:\n"
            "```json\n"
            '{"create_issue": true, "title": "Sorunun KÄ±sa BaÅŸlÄ±ÄŸÄ±", "labels": ["bug", "security"]}\n'
            "```\n"
            "Etiketleri (labels) sorunun tÃ¼rÃ¼ne gÃ¶re ('bug', 'security', 'performance', 'architecture') mantÄ±klÄ± ÅŸekilde seÃ§ebilirsin."
        )
    else:
        system_prompt = (
            "Sen hÄ±zlÄ± ve pratik bir Code Reviewer'sÄ±n. Bu diff'i bariz bug'lar, typo'lar ve basit stil hatalarÄ± iÃ§in incele. "
            "Ã‡ok kÄ±sa ve net ol. Gereksiz gevezelik yapma. Sadece hatayÄ± gÃ¶ster ve geliÅŸtiricinin kopyalayabilmesi iÃ§in DOÄRU KODU (Auto-Fix) yaz."
        )

    if custom_rules:
        system_prompt += f"\n\nAYRICA DÄ°KKAT ETMEN GEREKEN ÅÄ°RKETE Ã–ZEL KURALLAR ÅUNLARDIR:\n{custom_rules}"

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"LÃ¼tfen ÅŸu diff'i incele:\n\n```diff\n{diff_text}\n```"}
            ],
            temperature=0.2,
            top_p=0.7,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"[ERROR] AI analiz hatasÄ± ({model_name}): {str(e)}"
