import os
import json
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core import process_webhook_event

def main():
    event_path = os.getenv('GITHUB_EVENT_PATH')
    event_name = os.getenv('GITHUB_EVENT_NAME')

    if not event_path or not os.path.exists(event_path):
        print('GitHub event path not found. Exiting.')
        sys.exit(1)

    with open(event_path, 'r', encoding='utf-8') as f:
        payload = json.load(f)

    result = process_webhook_event(event_name, payload)
    
    if result.get('status') == 'error':
        sys.exit(1)

if __name__ == '__main__':
    main()

