from gmail_reader import get_latest_email
from classify import predict_intent
from extract_datetime import extract_datetime
from utils import split_sentences
from task_extractor import extract_tasks
from calendar_add import add_task_to_calendar

# --------------------------------------------------
# 1️⃣ Read latest unread email
# --------------------------------------------------
email_text, email_sent_time = get_latest_email()

if not email_text:
    print("No unread emails.")
    exit()

# --------------------------------------------------
# 2️⃣ Predict main intent
# --------------------------------------------------
intent, confidence = predict_intent(email_text)

# --------------------------------------------------
# 3️⃣ NLP extraction
# --------------------------------------------------
sentences = split_sentences(email_text)
tasks = extract_tasks(sentences, email_sent_time)

meeting_time = extract_datetime(email_text, email_sent_time)

# --------------------------------------------------
# 4️⃣ Print analysis (NO ACTION HERE)
# --------------------------------------------------
print("\n========== EMAIL ANALYSIS ==========")
print("Main intent :", intent)
print("Confidence  :", round(confidence, 3))

if meeting_time:
    print("Meeting detected at:", meeting_time)

for t in tasks:
    print("- Task:", t["task"])
    print("  Date:", t["date"])
    print("  Time:", t["time"])

# --------------------------------------------------
# 5️⃣ Schedule meeting (ONCE)
# --------------------------------------------------
if intent == "meeting" and meeting_time:
    print("\n📅 Scheduling meeting...")
    add_task_to_calendar(
        task_title="Review Meeting",
        date=meeting_time.date().isoformat(),
        time_str=meeting_time.time().strftime("%H:%M")
    )

# --------------------------------------------------
# 6️⃣ Schedule ALL tasks
# --------------------------------------------------
for t in tasks:
    if t["date"] and t["time"]:
        print("\n📌 Scheduling task:", t["task"][:60])
        add_task_to_calendar(
            task_title=t["task"],
            date=t["date"],
            time_str=t["time"]
        )
