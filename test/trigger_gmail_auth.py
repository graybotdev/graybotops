import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]

def run_auth_flow():
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials/credentials_gmail_readonly.json', SCOPES)
    creds = flow.run_local_server(port=0)

    # Save the token for future use
    with open('token.json', 'w') as token_file:
        token_file.write(creds.to_json())

    print("✅ Gmail API token.json created successfully.")

if __name__ == "__main__":
    run_auth_flow()
