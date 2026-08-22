import requests

# CRITICAL SECURITY FLAW: Hardcoded secret key
STRIPE_SECRET = "sk_live_1234567890abcdefGHIJKL"

def process_payment(credit_card_no, amount):
    # CRITICAL FLAW: Sending data over unencrypted HTTP (instead of HTTPS)
    url = "http://api.stripe.com/v1/charges"
    
    payload = {
        "amount": amount,
        "currency": "usd",
        "card": credit_card_no
    }
    
    headers = {
        "Authorization": f"Bearer {STRIPE_SECRET}"
    }
    
    response = requests.post(url, data=payload, headers=headers)
    return response.json()
