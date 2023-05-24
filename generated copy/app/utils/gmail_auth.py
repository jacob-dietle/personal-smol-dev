import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

def get_gmail_credentials():
    creds = None
    token_path = "token.pickle"
    creds_path = "client_secrets.json"
    scopes = ["https://www.googleapis.com/auth/gmail.modify"]

    if os.path.exists(token_path):
        with open(token_path, "rb") as token:
            creds = Credentials.from_authorized_user_file(token_path, scopes)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, scopes)
            creds = flow.run_local_server(port=0)

        with open(token_path, "wb") as token:
            token.write(creds.to_json().encode("utf-8"))

    return creds
