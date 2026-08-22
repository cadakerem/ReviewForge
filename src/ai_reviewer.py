import os
from openai import OpenAI

# Multi-Provider Configuration
AI_PROVIDER = os.getenv("AI_PROVIDER", "nvidia").lower()  # openai, nvidia, groq, gemini
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
        return f"[MOCK REVIEW] AI_API_KEY not configured, analysis simulated. ({mode})"

    model_name = DEEP_MODEL if mode == "DEEP_ANALYSIS" else LIGHT_MODEL

    if mode == "DEEP_ANALYSIS":
        system_prompt = (
            "You are a senior Security Engineer and Software Architect. "
            "Deeply analyze the following code diff for critical security vulnerabilities, architectural flaws, and performance issues.\n\n"
            "IMPORTANT RULE: Do not just point out the problem. Always provide the FIXED CODE BLOCK "
            "that the developer can copy-paste to resolve the issue immediately.\n\n"
            "ISSUE RULE: If you find a definitive, CRITICAL bug that could crash or compromise the project, "
            "you MUST append the following JSON block at the very end of your response:\n"
            "```json\n"
            '{"create_issue": true, "title": "Short Issue Title", "labels": ["bug", "security"]}\n'
            "```\n"
            "Choose labels intelligently based on the type of issue: 'bug', 'security', 'performance', or 'architecture'."
        )
    else:
        system_prompt = (
            "You are a fast and pragmatic Code Reviewer. "
            "Review this diff for obvious bugs, typos, and simple style issues. "
            "Be very brief and direct. No unnecessary explanation. "
            "Always show the correct fixed code (Auto-Fix) so the developer can copy it."
        )

    if custom_rules:
        system_prompt += f"\n\nADDITIONAL PROJECT-SPECIFIC RULES YOU MUST ENFORCE:\n{custom_rules}"

    try:
        completion = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Please review the following diff:\n\n```diff\n{diff_text}\n```"}
            ],
            temperature=0.2,
            top_p=0.7,
            max_tokens=1024
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"[ERROR] AI analysis failed ({model_name}): {str(e)}"
