import hmac
import hashlib
import os

# GÃ¼venli bir ÅŸekilde environment variable Ã¼zerinden okunmalÄ±.
GITHUB_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    if not GITHUB_SECRET:
        # Secret yapÄ±landÄ±rÄ±lmamÄ±ÅŸsa local test iÃ§indir, geÃ§ici olarak izin ver (prod iÃ§in deÄŸiÅŸtirilmeli)
        return True
    
    if not signature_header:
        return False
        
    hash_object = hmac.new(GITHUB_SECRET.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)
