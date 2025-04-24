import os
import glob
import sys
import json
import csv
import time
from datetime import datetime

# Setup imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.email_reader import read_recent_messages, save_to_json
from app.gpt_replies import build_prompt
from app.firework_client import run_firework_model
from app.gmail_service import send_email  # ✅ Gmail sender
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

# Trigger vocab
TRIGGER_STATUSES = [
    "ready", "available", "loaded", "call", "tracking", "update", "in transit", "status",
    "delay", "delayed", "arrived", "en route", "checked in", "waiting", "detention", "layover",
    "invoice", "payment", "paid", "unpaid", "past due", "remit", "remittance", "accessorial",
    "lumper", "bol", "bill of lading", "pod", "proof of delivery", "receipt", "proof", "driver",
    "drop", "pickup", "pu", "del", "eta", "appointment", "check call", "where's the truck", "location"
]

LOG_FILE = os.path.join(os.path.dirname(__file__), "email_log.csv")

def generate_reply(parsed_data, model="firework"):
    prompt = build_prompt(parsed_data)

    if model == "firework":
        print("⚡ Trying Firework AI...")
        start = time.time()
        firework_response = run_firework_model(prompt)
        duration = round(time.time() - start, 2)

        if firework_response:
            print(f"✅ Firework Success in {duration}s")
            return firework_response, "Firework"

        print("❌ Firework failed, falling back to GPT...")

    # GPT fallback
    try:
        start = time.time()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful logistics assistant replying to emails."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=300
        )
        duration = round(time.time() - start, 2)
        print(f"✅ GPT Success in {duration}s")
        return response.choices[0].message.content.strip(), "GPT"
    except Exception as e:
        print(f"🚨 GPT fallback failed too: {e}")
        return None, "None"

# Step 1: Read unread Gmail emails
messages = read_recent_messages()
save_to_json(messages)

# Step 2: Load latest parsed results
files = sorted(glob.glob("test/parsed_results_*.json"), key=os.path.getmtime, reverse=True)
FILENAME = files[0] if files else None

if not FILENAME:
    print("❌ No parsed results found.")
    exit()

with open(FILENAME, "r", encoding="utf-8") as f:
    parsed_messages = json.load(f)

# Step 3: Ensure log file exists
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, mode="w", newline="", encoding="utf-8") as log:
        writer = csv.writer(log)
        writer.writerow(["timestamp", "to_email", "subject", "model_used", "response"])

# Step 4: Process and respond to messages
for msg in parsed_messages:
    body = msg.get("body", "").lower()
    subject = msg.get("subject", "").lower()
    content = f"{subject} {body}"

    to_email = msg.get("from", "").strip()
    subject_line = msg.get("subject", "").strip()
    thread_id = msg.get("thread_id", None)

    if (
        not to_email or
        "mailer-daemon" in to_email.lower() or
        "noreply" in to_email.lower() or
        "delivery status notification" in subject
    ):
        print(f"⚠️ Skipping invalid or automated email: {to_email} | Subject: {subject_line}")
        continue

    if any(trigger in content for trigger in TRIGGER_STATUSES):
        reply, model_used = generate_reply(msg, model="firework")

        if reply:
            print(f"📨 Reply ready for {to_email} using {model_used}")
            print(reply)

            # ✅ Send reply via Gmail
            send_email(to_email, subject_line, reply, thread_id=thread_id)

            # 📁 Log to CSV
            with open(LOG_FILE, mode="a", newline="", encoding="utf-8") as log:
                writer = csv.writer(log)
                writer.writerow([
                    datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
                    to_email,
                    subject_line,
                    model_used,
                    reply
                ])
        else:
            print(f"🚨 No reply generated for {to_email} | Subject: {subject_line}")
    else:
        print(f"❌ No trigger match — skipping: {subject_line}")
