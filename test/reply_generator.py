import json
import glob
import os
from datetime import datetime

# Load the most recent parsed JSON file
files = sorted(glob.glob("parsed_results_*.json"), key=os.path.getmtime, reverse=True)
FILENAME = files[0] if files else None

if not FILENAME:
    print("❌ No parsed_results_*.json found.")
    exit()

with open(FILENAME, "r", encoding="utf-8") as f:
    data = json.load(f)

# Function to generate a reply message
def generate_reply(entry):
    load_id = entry.get("load_id", "the load")
    if entry.get("doc_type_requested") == "POD":
        return f"Hi, just sent over the POD for Load {load_id}. Let us know if anything else is needed."
    
    if entry.get("status") == "Rate Confirmation Received":
        return f"Thanks, we received the signed rate confirmation for Load {load_id}. We'll proceed accordingly."
    
    if entry.get("status") == "Delayed" and entry.get("new_eta"):
        return f"Thanks for the update. Noted the new ETA for Load {load_id} as {entry['new_eta']}."
    
    if entry.get("status") == "Rolling" and entry.get("driver_name"):
        return f"Thanks {entry['driver_name']}, tracking you en route for Load {load_id}. Stay safe."
    
    return f"Thanks for the update regarding Load {load_id}. We’ve noted the status as '{entry.get('status')}'."

# Generate and display replies
print("\n📬 GrayBot Human-Like Email Replies:\n")
for entry in data:
    reply = generate_reply(entry)
    print(f"✉️ Reply for Load {entry.get('load_id')}:")
    print(reply)
    print("=" * 60)
