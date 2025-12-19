from flask import Flask, request, render_template_string
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
import os
import pickle
from datetime import timezone
from threading import Thread
import webbrowser
from datetime import time


SCOPES = ["https://www.googleapis.com/auth/calendar"]

app = Flask(__name__)

# in‑memory store for latest conflict info
LAST_CONFLICT = {}


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


@app.route("/conflict", methods=["GET"])
def conflict_page():
    data = LAST_CONFLICT.get("data")
    if not data:
        return "No conflict data", 400

    events = [
        {
            "summary": ev.get("summary"),
            "start": ev["start"].get("dateTime") or ev["start"].get("date"),
        }
        for ev in data["conflicts"]
    ]

    html = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Calendar Conflict</title>
  <style>
    :root {
      --bg: #020617;
      --bg-elevated: #020617;
      --border-subtle: #1f2937;
      --accent: #6366f1;
      --accent-soft: rgba(99, 102, 241, 0.15);
      --accent-strong: #4f46e5;
      --danger: #ef4444;
      --danger-soft: rgba(239, 68, 68, 0.12);
      --success: #22c55e;
      --text-main: #e5e7eb;
      --text-muted: #9ca3af;
      --chip-bg: #0b1120;
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    body {
  min-height: 100vh;
  background: radial-gradient(circle at top, #1d283a 0, #020617 45%);
  color: var(--text-main);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 10px;   /* was 24px */
}
    .shell {
      max-width: 720px;
      width: 100%;
      background: linear-gradient(145deg, #020617 0, #020617 30%, #020617 100%);
      border-radius: 18px;
      border: 1px solid rgba(148, 163, 184, 0.18);
      box-shadow:
        0 22px 55px rgba(15, 23, 42, 0.85),
        0 0 0 1px rgba(15, 23, 42, 0.9);
      overflow: hidden;
      backdrop-filter: blur(14px);
    }

    .shell-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 14px 18px;
      background: radial-gradient(circle at top left, rgba(99, 102, 241, 0.25), transparent 55%);
      border-bottom: 1px solid rgba(148, 163, 184, 0.2);
    }

    .traffic-lights {
      display: flex;
      gap: 7px;
    }

    .dot {
      width: 10px;
      height: 10px;
      border-radius: 999px;
    }
    .dot.red { background: #f97373; }
    .dot.yellow { background: #facc15; }
    .dot.green { background: #22c55e; }

    .title-group {
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .title-main {
      font-size: 15px;
      font-weight: 600;
      letter-spacing: 0.01em;
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .title-pill {
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      border: 1px solid rgba(129, 140, 248, 0.5);
    }

    .title-sub {
      font-size: 11px;
      color: var(--text-muted);
    }

    .shell-body {
      padding: 18px 20px 20px 20px;
      display: grid;
      grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
      gap: 18px;
    }

    .section-label {
      font-size: 11px;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--text-muted);
      margin-bottom: 6px;
    }

    .slot-card {
      border-radius: 14px;
      background: radial-gradient(circle at top left, rgba(79, 70, 229, 0.15), #020617 65%);
      border: 1px solid rgba(129, 140, 248, 0.35);
      padding: 12px 14px;
    }

    .slot-chip {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 9px;
      border-radius: 999px;
      font-size: 11px;
      background: rgba(15, 23, 42, 0.8);
      border: 1px solid rgba(148, 163, 184, 0.4);
      color: var(--text-main);
      margin-bottom: 6px;
    }

    .slot-chip-dot {
      width: 8px;
      height: 8px;
      border-radius: 999px;
      background: var(--accent);
      box-shadow: 0 0 0 4px var(--accent-soft);
    }

    .slot-main {
      font-size: 13px;
      font-weight: 500;
    }

    .slot-sub {
      font-size: 11px;
      color: var(--text-muted);
      margin-top: 3px;
    }

    .events-card {
      border-radius: 14px;
      background: var(--bg-elevated);
      border: 1px solid var(--border-subtle);
      padding: 12px 14px;
    }

    .events-list {
      list-style: none;
      margin-top: 4px;
    }

    .event-item {
      padding: 8px 0;
      border-bottom: 1px solid rgba(15, 23, 42, 0.95);
      display: flex;
      flex-direction: column;
      gap: 2px;
    }

    .event-item:last-child {
      border-bottom: none;
    }

    .event-summary {
      font-size: 13px;
      font-weight: 500;
      color: var(--text-main);
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .event-tag {
      font-size: 10px;
      padding: 1px 6px;
      border-radius: 999px;
      background: rgba(15, 23, 42, 0.9);
      border: 1px solid rgba(55, 65, 81, 0.9);
      color: var(--text-muted);
    }

    .event-time {
      font-size: 11px;
      color: var(--text-muted);
    }

    .actions-card {
      margin-top: 6px;
      border-radius: 14px;
      background: radial-gradient(circle at top, rgba(15, 23, 42, 0.85), #020617 60%);
      border: 1px solid rgba(55, 65, 81, 0.9);
      padding: 12px 14px 10px 14px;
    }

    .actions-title {
      font-size: 12px;
      font-weight: 500;
      margin-bottom: 7px;
    }

    .actions-grid {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 8px;
    }

    .btn {
      border-radius: 10px;
      border: 0;
      padding: 8px 9px;
      font-size: 12px;
      font-weight: 500;
      cursor: pointer;
      display: flex;
      flex-direction: column;
      gap: 2px;
      align-items: flex-start;
      transition: transform 0.05s ease-out, box-shadow 0.1s ease-out, background 0.15s ease-out;
      text-align: left;
    }

    .btn:active {
      transform: translateY(1px);
      box-shadow: none;
    }

    .btn-label {
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .btn-label span.icon {
      font-size: 13px;
    }

    .btn-hint {
      font-size: 10px;
      color: var(--text-muted);
    }

    .btn-delete {
      background: var(--danger-soft);
      color: var(--danger);
      box-shadow: 0 8px 20px rgba(127, 29, 29, 0.5);
    }

    .btn-delete:hover {
      background: rgba(248, 113, 113, 0.18);
    }

    .btn-reschedule {
      background: rgba(16, 185, 129, 0.14);
      color: #22c55e;
      box-shadow: 0 8px 20px rgba(6, 95, 70, 0.6);
    }

    .btn-reschedule:hover {
      background: rgba(16, 185, 129, 0.2);
    }

    .btn-also {
      background: rgba(30, 64, 175, 0.15);
      color: #60a5fa;
      box-shadow: 0 8px 20px rgba(30, 64, 175, 0.6);
    }

    .btn-also:hover {
      background: rgba(37, 99, 235, 0.22);
    }

    .footer-hint {
      margin-top: 8px;
      font-size: 10px;
      color: var(--text-muted);
      display: flex;
      justify-content: space-between;
      gap: 8px;
    }

    .footer-hint span {
      opacity: 0.85;
    }

    @media (max-width: 700px) {
      .shell-body {
        grid-template-columns: 1fr;
      }
    }
  </style>
</head>
<body>
  <div class="shell">
    <div class="shell-header">
      <div class="traffic-lights">
        <div class="dot red"></div>
        <div class="dot yellow"></div>
        <div class="dot green"></div>
      </div>
      <div class="title-group">
        <div class="title-main">
          Calendar conflict
          <span class="title-pill">Google Calendar · Asia/Kolkata</span>
        </div>
        <div class="title-sub">Choose how to handle overlapping events at this time slot.</div>
      </div>
      <div style="width:24px;"></div>
    </div>

    <div class="shell-body">
      <div>
        <div class="section-label">Selected slot</div>
        <div class="slot-card">
          <div class="slot-chip">
            <div class="slot-chip-dot"></div>
            <span>New task window</span>
          </div>
          <div class="slot-main">
            {{ start }} → {{ end }}
          </div>
          <div class="slot-sub">
            The new task will be scheduled in this 30‑minute range.
          </div>
        </div>
      </div>

      <div>
        <div class="section-label">Existing events</div>
        <div class="events-card">
          <ul class="events-list">
            {% for ev in events %}
            <li class="event-item">
              <div class="event-summary">
                {{ ev.summary or "No title" }}
                <span class="event-tag">Busy</span>
              </div>
              <div class="event-time">{{ ev.start }}</div>
            </li>
            {% endfor %}
          </ul>
        </div>
      </div>
    </div>

    <form method="post" action="/resolve">
      <div class="shell-body" style="padding-top: 0; border-top: 1px solid rgba(31, 41, 55, 0.9);">
        <div class="actions-card" style="grid-column: 1 / -1;">
          <div class="actions-title">How do you want to resolve this?</div>
          <div class="actions-grid">
            <button class="btn btn-delete" name="action" value="delete">
              <div class="btn-label"><span class="icon">✂️</span><span>Delete previous</span></div>
              <div class="btn-hint">Remove existing events and keep only the new task.</div>
            </button>

            <button class="btn btn-reschedule" name="action" value="reschedule">
              <div class="btn-label"><span class="icon">⏱️</span><span>Reschedule both</span></div>
              <div class="btn-hint">Shift existing and new tasks by +30 minutes.</div>
            </button>

            <button class="btn btn-also" name="action" value="also_add">
              <div class="btn-label"><span class="icon">➕</span><span>Also add</span></div>
              <div class="btn-hint">Keep all events in this slot (double‑book).</div>
            </button>
          </div>
          <div class="footer-hint">
            <span>Tip: you can always adjust times later directly in Google Calendar.</span>
            <span>Changes apply only to this time window.</span>
          </div>
        </div>
      </div>
    </form>
  </div>
</body>
</html>
"""



    return render_template_string(
        html,
        start=data["start"],
        end=data["end"],
        events=events,
    )


@app.route("/resolve", methods=["POST"])
def resolve_conflict():
    action = request.form.get("action")
    data = LAST_CONFLICT.get("data")
    if not data:
        return "No conflict data", 400

    service = get_calendar_service()
    calendar_id = "primary"

    start = datetime.fromisoformat(data["start"])
    end = datetime.fromisoformat(data["end"])
    conflicts = data["conflicts"]

    if action == "delete":
        for ev in conflicts:
            service.events().delete(
                calendarId=calendar_id,
                eventId=ev["id"],
            ).execute()

    elif action == "reschedule":
    # Fixed slots
      base_date = start.date()
      existing_start = datetime.combine(base_date, time(9, 0), tzinfo=start.tzinfo)
      existing_end   = datetime.combine(base_date, time(9, 30), tzinfo=start.tzinfo)

      new_start = datetime.combine(base_date, time(9, 30), tzinfo=start.tzinfo)
      new_end = datetime.combine(base_date, time(10, 0), tzinfo=start.tzinfo)

    #1️ ⁇  Move existing conflicting events to 09:00–09:30
      for ev in conflicts:
        ev["start"]["dateTime"] = existing_start.isoformat()
        ev["end"]["dateTime"] = existing_end.isoformat()

        service.events().update(
            calendarId=calendar_id,
            eventId=ev["id"],
            body=ev
        ).execute()

    elif action == "also_add":
        pass

    event_body = {
        "summary": data["task_title"][:100],
        "start": {
            "dateTime": start.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
        "end": {
            "dateTime": end.isoformat(),
            "timeZone": "Asia/Kolkata",
        },
    }

    created = service.events().insert(
        calendarId=calendar_id,
        body=event_body,
    ).execute()

    LAST_CONFLICT.clear()

    event_link = created.get("htmlLink", "#")

    success_html = f"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <title>Event created</title>
      <style>
        :root {{
          --bg: #020617;
          --accent: #22c55e;
          --accent-soft: rgba(34, 197, 94, 0.14);
          --accent-strong: #16a34a;
          --text-main: #e5e7eb;
          --text-muted: #9ca3af;
        }}
        * {{
          box-sizing: border-box;
          margin: 0;
          padding: 0;
          font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }}
        body {{
          min-height: 100vh;
          background: radial-gradient(circle at top, #1d283a 0, #020617 45%);
          color: var(--text-main);
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 24px;
        }}
        .card {{
          max-width: 520px;
          width: 100%;
          border-radius: 18px;
          background: linear-gradient(145deg, #020617 0, #020617 70%, #020617 100%);
          border: 1px solid rgba(34, 197, 94, 0.35);
          box-shadow:
            0 24px 60px rgba(15, 23, 42, 0.9),
            0 0 0 1px rgba(15, 23, 42, 0.9);
          padding: 20px 22px 18px 22px;
        }}
        .header {{
          display: flex;
          align-items: center;
          gap: 10px;
          margin-bottom: 10px;
        }}
        .icon-circle {{
          width: 30px;
          height: 30px;
          border-radius: 999px;
          background: var(--accent-soft);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 18px;
          color: var(--accent);
          box-shadow: 0 0 0 6px rgba(34, 197, 94, 0.15);
        }}
        .title-main {{
          font-size: 16px;
          font-weight: 600;
        }}
        .title-sub {{
          font-size: 12px;
          color: var(--text-muted);
        }}
        .body {{
          margin-top: 12px;
          font-size: 13px;
          line-height: 1.5;
        }}
        .field {{
          margin-top: 10px;
          padding: 9px 10px;
          border-radius: 10px;
          background: rgba(15, 23, 42, 0.9);
          border: 1px solid rgba(55, 65, 81, 0.9);
          font-size: 12px;
          color: var(--text-muted);
        }}
        .field span.label {{
          font-weight: 500;
          color: var(--text-main);
        }}
        .actions {{
          margin-top: 14px;
          display: flex;
          justify-content: space-between;
          gap: 10px;
          align-items: center;
        }}
        .btn-link {{
          padding: 8px 12px;
          border-radius: 999px;
          border: 0;
          background: var(--accent-soft);
          color: var(--accent-strong);
          font-size: 13px;
          font-weight: 500;
          text-decoration: none;
          display: inline-flex;
          align-items: center;
          gap: 6px;
          cursor: pointer;
          transition: background 0.15s, transform 0.05s;
        }}
        .btn-link:hover {{
          background: rgba(34, 197, 94, 0.22);
        }}
        .btn-link:active {{
          transform: translateY(1px);
        }}
        .hint {{
          font-size: 11px;
          color: var(--text-muted);
        }}
      </style>
    </head>
    <body>
      <div class="card">
        <div class="header">
          <div class="icon-circle">✓</div>
          <div>
            <div class="title-main">Event created successfully</div>
            <div class="title-sub">Your choice has been applied in Google Calendar.</div>
          </div>
        </div>

        <div class="body">
          <div class="field">
            <span class="label">Task:</span>
            <br>{{ data["task_title"] }}
          </div>
          <div class="field">
            <span class="label">Time:</span>
            <br>{{ start.isoformat() }} → {{ end.isoformat() }}
          </div>
        </div>

        <div class="actions">
          <a class="btn-link" href="{event_link}" target="_blank" rel="noopener noreferrer">
            Open in Google Calendar →
          </a>
          <div class="hint">You can close this tab after reviewing the event.</div>
        </div>
      </div>
    </body>
    </html>
    """

    from flask import render_template_string
    return render_template_string(success_html, data=data, start=start, end=end)



def handle_conflict(task_title, start, end, conflicts):
    """
    Called from calendar_add.py when a conflict is detected.
    Stores conflict data, starts Flask (once), opens the /conflict page.
    """
    print("handle_conflict called")

    LAST_CONFLICT["data"] = {
        "task_title": task_title,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "conflicts": conflicts,
    }

    def run_app():
        app.run(host="127.0.0.1", port=5001, debug=False)

    if not getattr(handle_conflict, "_started", False):
        handle_conflict._started = True
        Thread(target=run_app, daemon=True).start()

    webbrowser.open_new("http://127.0.0.1:5001/conflict")
