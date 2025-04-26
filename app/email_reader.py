import os
import io
import base64
import pickle
import re
import json
import tempfile
from datetime import datetime
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

TOKEN_PICKLE = "token.pickle"

def get_service():
    creds = None

    # Step 1: Try loading local token
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, 'rb') as token_file:
            creds = pickle.load(token_file)

    # Step 2: If no local token, load from environment
    if not creds:
        token_base64 = os.getenv("TOKEN_PICKLE_BASE64")
        if not token_base64:
            raise ValueError("TOKEN_PICKLE_BASE64 environment variable not set.")

        token_bytes = base64.b64decode(token_base64)
        creds = pickle.loads(token_bytes)

        # Optional: Save token locally for faster future runs
        with open(TOKEN_PICKLE, 'wb') as f:
            f.write(token_bytes)

    # Step 3: If token expired, refresh it
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

    return build('gmail', 'v1', credentials=creds)


def read_recent_messages(query=None, max_results=25):
    service = get_service()

    query = query or (
        'is:unread ('
        'subject:("Load" OR "Rate Confirmation" OR "Broker" OR "Update" OR "Delayed" '
        'OR "Accessorial" OR "Detention" OR "Lumper" OR "BOL" OR "Bill of Lading" '
        'OR "Status" OR "Invoice" OR "Payment") '
        'OR has:attachment)'
    )

    results = service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
    messages = results.get('messages', [])

    email_data = []

    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        payload = msg_detail['payload']
        headers = payload.get("headers", [])

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "No Subject")

        from_email = ""
        for h in headers:
            if h["name"].lower() in ["from", "reply-to", "return-path"]:
                if not from_email:
                    match = re.search(r'<(.+?)>', h['value'])
                    from_email = match.group(1) if match else h['value'].strip()

        parts = payload.get("parts", [])
        body = ""

        if parts:
            for part in parts:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    body = base64.urlsafe_b64decode(part['body']['data']).decode()
                    break
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode()

        service.users().messages().modify(
            userId='me',
            id=msg['id'],
            body={'removeLabelIds': ['UNREAD']}
        ).execute()

        thread_id = msg_detail.get("threadId")

        email_data.append({
            "subject": subject,
            "body": body,
            "from": from_email,
            "threadId": thread_id,
        })

    return email_data


def save_to_json(messages):
    if not messages:
        print("❌ No messages found.")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test/parsed_results_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)

    print(f"✅ {len(messages)} messages saved to {output_file}")


if __name__ == "__main__":
    messages = read_recent_messages()
    save_to_json(messages)
