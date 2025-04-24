import pandas as pd
import json
import glob
import os

# 🧠 Auto-locate the most recent results file
files = sorted(glob.glob("parsed_results_*.json"), key=os.path.getmtime, reverse=True)
FILENAME = files[0] if files else None

if not FILENAME:
    print("❌ No parsed_results_*.json files found.")
    exit()

# ✅ Load latest JSON file
with open(FILENAME, "r", encoding="utf-8") as file:
    data = json.load(file)

df = pd.DataFrame(data)

# 📊 Display only key columns
cols = [
    "load_id", "status", "eta", "pickup_date", "pickup_time",
    "delivery_date", "delivery_time", "route", "location", "doc_type_requested"
]

print("\n📊 Parsed Load Email Summary:\n")
print(df[cols].fillna("").to_string(index=False))
