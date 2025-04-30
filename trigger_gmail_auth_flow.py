import os
import pickle
import pathlib

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Define the path to your credentials file
CREDENTIALS_FILE = "credentials/credentials_gmail_readonly.json"
TOKEN_FILE = "credentials/token.pickle"

# Scope for Gmail read-only access
SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]

def main():
    creds = None

    # If token.pickle exists, load it
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "rb") as token:
            creds = pickle.load(token)

    # If there are no valid credentials, launch the browser auth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the new token
        os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
        with open(TOKEN_FILE, "wb") as token:
            pickle.dump(creds, token)

    print("✅ Gmail token authentication successful. New token.pickle created.")

if __name__ == "__main__":
    main()
