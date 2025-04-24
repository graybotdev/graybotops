# app/gmail_service.py

import os
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Unified scopes for full Gmail access (send, read, modify)
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

def create_gmail_service():
    # Load Gmail token authorized with the above scopes
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    service = build('gmail', 'v1', credentials=creds)
    return service

def send_email(to_email, subject, message_body, thread_id=None):
    service = create_gmail_service()

    message = MIMEText(message_body)
    message['to'] = to_email
    message['subject'] = subject
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    send_body = {'raw': raw_message}
    if thread_id:
        send_body['threadId'] = thread_id

    response = service.users().messages().send(
        userId='me',
        body=send_body
    ).execute()

    return response
