from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os
import base64
from email import message_from_bytes
from email.utils import parsedate_to_datetime

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def get_gmail_service():
    creds = None

    if os.path.exists("gmail_token.pickle"):
        with open("gmail_token.pickle", "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)

        with open("gmail_token.pickle", "wb") as f:
            pickle.dump(creds, f)

    return build("gmail", "v1", credentials=creds)

def get_latest_email():
    service = get_gmail_service()

    results = service.users().messages().list(
        userId="me",
        maxResults=1,
        q="is:unread"
    ).execute()

    messages = results.get("messages", [])
    if not messages:
        return None, None

    msg = service.users().messages().get(
        userId="me",
        id=messages[0]["id"],
        format="raw"
    ).execute()

    raw = base64.urlsafe_b64decode(msg["raw"])
    email_msg = message_from_bytes(raw)

    subject = email_msg.get("Subject", "")
    date_header = email_msg.get("Date")

    # Parse sent date
    sent_time = parsedate_to_datetime(date_header)

    body = ""
    if email_msg.is_multipart():
        for part in email_msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode(errors="ignore")
                break
    else:
        body = email_msg.get_payload(decode=True).decode(errors="ignore")

    return subject + "\n" + body, sent_time