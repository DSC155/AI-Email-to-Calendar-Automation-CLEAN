import pandas as pd
import random

INPUT_FILE = "emails.csv"      # Enron CSV
OUTPUT_FILE = "enron_500_full_emails.csv"

# Load only required columns
df = pd.read_csv(INPUT_FILE, usecols=["file", "message"])

# Drop empty emails
df = df.dropna()
df = df[df["message"].str.len() > 200]

# Shuffle and sample 500
sampled = df.sample(n=500, random_state=42)

# Save
sampled.to_csv(OUTPUT_FILE, index=False)

print("Saved 500 full emails to", OUTPUT_FILE)
