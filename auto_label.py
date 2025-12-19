import pandas as pd

INPUT_FILE = "enron_500_full_emails.csv"
OUTPUT_FILE = "enron_500_labeled.csv"

def label_email(text):
    t = text.lower()

    meeting_words = [
        "meeting", "meet", "call", "schedule", "conference", "zoom"
    ]

    task_words = [
        "please", "submit", "complete", "finish", "send", "check", "review"
    ]

    if any(w in t for w in meeting_words):
        return "meeting"

    if any(w in t for w in task_words):
        return "task"

    return "informational"

df = pd.read_csv(INPUT_FILE)
df["label"] = df["message"].apply(label_email)

df.to_csv(OUTPUT_FILE, index=False)

print("✅ Labels added using keywords")
