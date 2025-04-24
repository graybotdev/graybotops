import json
import glob
import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from app.firework_client import run_firework_model

load_dotenv()
client = OpenAI()

# 🧠 Load latest parsed results
files = sorted(glob.glob("parsed_results_*.json"), key=os.path.getmtime, reverse=True)
FILENAME = files[0] if files else None

if not FILENAME:
    print("❌ No parsed_results_*.json found.")
    exit()

with open(FILENAME, "r", encoding="utf-8") as file:
    messages = json.load(file)

def build_prompt(parsed_data):
    return f"""
You are GrayBot, a professional logistics assistant at a freight brokerage.

You **advocate for truck drivers and carriers** — your tone is friendly, professional, and concise. Always respect their time, communicate delays clearly, and ensure brokers are being transparent and fair.

Never sound robotic. Speak like a helpful teammate who understands the stress of the road and wants to make operations smooth for drivers.

Parsed email data:
{json.dumps(parsed_data, indent=2)}
"""

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
        else:
            print("❌ Firework failed, falling back to GPT...")

    # GPT fallback or primary
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

# 🗣️ Generate replies
print("\n🤖 GrayBot AI-Powered Replies:\n")
for entry in messages:
    reply, model_used = generate_reply(entry, model="firework")
    print(f"✉️ Reply for Load {entry.get('load_id', 'N/A')} [via {model_used}]:")
    print(reply)
    print("=" * 80)
