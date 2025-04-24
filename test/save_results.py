import json
import csv
from app.email_reader import read_recent_messages
from app.parser import parse_email
from datetime import datetime

def save_to_csv(data, filename="parsed_results.csv"):
    keys = data[0].keys()
    with open(filename, mode="w", newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(data)

def save_to_json(data, filename="parsed_results.json"):
    with open(filename, mode="w", encoding='utf-8') as file:
        json.dump(data, file, indent=4)

if __name__ == "__main__":
    all_parsed = []

    messages = read_recent_messages()
    for msg in messages:
        parsed_list = parse_email(msg["subject"], msg["body"])
        for parsed_data in parsed_list:
            parsed_data["from"] = msg.get("from")  # ✅ Add sender email to parsed data
            all_parsed.append(parsed_data)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_to_csv(all_parsed, f"parsed_results_{timestamp}.csv")
    save_to_json(all_parsed, f"parsed_results_{timestamp}.json")

    print(f"✅ Saved {len(all_parsed)} parsed entries to CSV and JSON.")
