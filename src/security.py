import hmac
import hashlib
import os

# Güvenli bir şekilde environment variable üzerinden okunmalı.
GITHUB_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    if not GITHUB_SECRET:
        # Secret yapılandırılmamışsa local test içindir, geçici olarak izin ver (prod için değiştirilmeli)
        return True
    
    if not signature_header:
        return False
        
    hash_object = hmac.new(GITHUB_SECRET.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)
