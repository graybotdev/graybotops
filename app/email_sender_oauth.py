import os
import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
import pickle
from dotenv import load_dotenv

load_dotenv()

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]
CLIENT_SECRET_FILE = os.getenv("GOOGLE_OAUTH2_CREDENTIAL_FILE")
TOKEN_PICKLE = "token.pickle"

def get_service():
    creds = None
    if os.path.exists(TOKEN_PICKLE):
        with open(TOKEN_PICKLE, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PICKLE, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)
    return service

def create_message(to, subject, body_text):
    message = MIMEText(body_text)
    message['to'] = to
    message['subject'] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_email(recipient, subject, body):
    try:
        print(f"[DEBUG] Sending to: {recipient} | Subject: {subject}")
        service = get_service()
        message = create_message(recipient, subject, body)
        print(f"[DEBUG] Built message: {message}")
        sent = service.users().messages().send(userId="me", body=message).execute()
        print(f"[DEBUG] Gmail API result: {sent}")
        return sent
    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")
        return None

