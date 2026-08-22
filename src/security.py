import hmac
import hashlib
import os

GITHUB_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET", "")

def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    # Fix #3: Fail-closed — if no secret is configured, deny all requests.
    if not GITHUB_SECRET:
        return False

    if not signature_header:
        return False

    hash_object = hmac.new(GITHUB_SECRET.encode("utf-8"), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = "sha256=" + hash_object.hexdigest()
    return hmac.compare_digest(expected_signature, signature_header)
