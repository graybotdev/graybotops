import os
import json
import pickle
import base64
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ✅ Load environment variables from .env file
load_dotenv()

# 🔐 Load Gmail credentials from base64-encoded token
TOKEN_BASE64 = os.getenv("TOKEN_PICKLE_BASE64")

def get_service():
    if not TOKEN_BASE64:
        raise ValueError("TOKEN_PICKLE_BASE64 environment variable not set.")

    token_data = base64.b64decode(TOKEN_BASE64)
    creds = pickle.loads(token_data)
    service = build('gmail', 'v1', credentials=creds)
    return service

def get_message_body(payload):
    parts = payload.get('parts')
    if parts:
        for part in parts:
            body = part.get('body', {}).get('data')
            if body:
                return base64.urlsafe_b64decode(body.encode('UTF-8')).decode('utf-8')
    else:
        body = payload.get('body', {}).get('data')
        if body:
            return base64.urlsafe_b64decode(body.encode('UTF-8')).decode('utf-8')
    return ""

def read_recent_messages():
    service = get_service()
    # Only unread emails, not sent by GrayBot itself
    results = service.users().messages().list(userId='me', q="is:unread -from:me").execute()
    messages = results.get('messages', [])

    emails = []
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()
        payload = msg['payload']
        headers = payload['headers']

        subject = ''
        sender = ''

        for header in headers:
            if header['name'].lower() == 'subject':
                subject = header['value']
            if header['name'].lower() == 'from':
                sender = header['value']

        body = get_message_body(payload)
        thread_id = msg.get('threadId')

        emails.append({
            "subject": subject,
            "from": sender,
            "body": body,
            "thread_id": thread_id
        })

        # ✅ Mark the message as read to prevent reprocessing
        service.users().messages().modify(
            userId='me',
            id=message['id'],
            body={'removeLabelIds': ['UNREAD']}
        ).execute()

    return emails

def save_to_json(messages, filename="test/parsed_results_temp.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)
