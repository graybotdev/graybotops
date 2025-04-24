import json
import glob
import os
from datetime import datetime
import sys
import csv

# Add parent directory to path for module imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.gpt_replies import generate_reply
from app.gmail_service import send_email
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Trigger words that indicate we should reply
TRIGGER_STATUSES = ["ready", "available", "loaded", "call", "tracking", "update", "in transit"]

# Get the latest parsed JSON file
files = sorted(glob.glob("parsed_results_*.json"), key=os.path.getmtime, reverse=True)
FILENAME = files[0] if files else None

if not FILENAME:
    print("❌ No parsed_results_*.json found.")
    exit()

with open(FILENAME, "r", encoding="utf-8") as file:
    messages = json.load(file)

# Define log path inside /test folder
log_file = os.path.join(os.path.dirname(__file__), "email_log.csv")

# Create CSV log file if it doesn't exist
if not os.path.exists(log_file):
    with open(log_file, mode="w", newline="", encoding="utf-8") as log:
        writer = csv.writer(log)
        writer.writerow(["timestamp", "to_email", "subject", "response"])

# Loop through parsed messages and send replies
for msg in messages:
    body = msg.get("body", "").lower()
    status_hit = any(trigger in body for trigger in TRIGGER_STATUSES)

    if status_hit:
        sender = msg.get("from", "").strip()
        subject = "RE: " + (msg.get("subject", "Load Update")).strip()
        reply = generate_reply(body)

        if sender and reply:
            print(f"📨 Sending to {sender} | Subject: {subject}")
            status, response = send_email(sender, subject, reply)

            with open(log_file, mode="a", newline="", encoding="utf-8") as log:
                writer = csv.writer(log)
                writer.writerow([datetime.utcnow(), sender, subject, reply])

            print(f"✅ Sent ({status}) | Response: {response}")
        else:
            print(f"⚠️ Missing sender or reply for message: {msg}")
