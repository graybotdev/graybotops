import os
import base64
import pickle
import re
import json
from datetime import datetime
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SCOPES = ['https://www.googleapis.com/auth/gmail.modify',
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

    return build('gmail', 'v1', credentials=creds)


def read_recent_messages(query=None, max_results=25):
    service = get_service()

    # Optional custom query to narrow results
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
       
        # 🟣 Mark email as read
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
