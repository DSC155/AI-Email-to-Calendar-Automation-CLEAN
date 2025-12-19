from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import pickle, os
from datetime import datetime, timedelta, timezone
import time
from conflict_server import handle_conflict

SCOPES = ["https://www.googleapis.com/auth/calendar"]


def get_calendar_service():
    creds = None
    if os.path.exists("calendar_token.pickle"):
        with open("calendar_token.pickle", "rb") as f:
            creds = pickle.load(f)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
        with open("calendar_token.pickle", "wb") as f:
            pickle.dump(creds, f)

    return build("calendar", "v3", credentials=creds)


def add_task_to_calendar(task_title, date,time_str):
    service = get_calendar_service()
    calendar_id = "primary"

    start = datetime.fromisoformat(f"{date}T{time_str}")

    end = start + timedelta(minutes=30)

    ist_offset = timedelta(hours=5, minutes=30)
    start_ist = start.replace(tzinfo=timezone(ist_offset))
    end_ist = end.replace(tzinfo=timezone(ist_offset))

    events_result = service.events().list(
        calendarId=calendar_id,
        timeMin=start_ist.isoformat(),
        timeMax=end_ist.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    conflicts = events_result.get("items", [])

    if conflicts:
        print("Conflict found, opening HTML popup...")
        handle_conflict(task_title, start_ist, end_ist, conflicts)
   
        while True:
            time.sleep(1)

    event = {
        "summary": task_title[:100],
        "start": {
            "dateTime": start_ist.isoformat(),
            "timeZone": "Asia/Kolkata"
        },
        "end": {
            "dateTime": end_ist.isoformat(),
            "timeZone": "Asia/Kolkata"
        }
    }

    created = service.events().insert(
        calendarId="primary",
        body=event
    ).execute()

    print("📅 Event created:", created.get("htmlLink"))
