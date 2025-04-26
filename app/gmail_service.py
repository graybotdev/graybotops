import os
import base64
import pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

SCOPES = [
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

def create_gmail_service():
    creds = None

    token_base64 = os.getenv("TOKEN_PICKLE_BASE64")
    if not token_base64:
        raise ValueError("TOKEN_PICKLE_BASE64 environment variable not set.")

    token_bytes = base64.b64decode(token_base64)
    creds = pickle.loads(token_bytes)

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())

    return build('gmail', 'v1', credentials=creds)

def send_email(to_email, subject, message_body, thread_id=None):
    service = create_gmail_service()

    message = {
        'raw': base64.urlsafe_b64encode(
            f"To: {to_email}\nSubject: {subject}\n\n{message_body}".encode("utf-8")
        ).decode("utf-8")
    }

    if thread_id:
        message['threadId'] = thread_id

    response = service.users().messages().send(userId='me', body=message).execute()
    return response
