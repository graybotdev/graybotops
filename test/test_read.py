from app.email_reader import read_recent_messages
from app.parser import parse_email

if __name__ == "__main__":
    messages = read_recent_messages()

    for msg in messages:
        print(f"From: {msg.get('from', 'Unknown')}")  # ✅ Show sender
        print(f"Subject: {msg['subject']}")
        print(msg['body'])
        print("=" * 50)

        parsed_data_list = parse_email(msg['subject'], msg['body'])  # ✅ Handle multi-load emails

        for parsed_data in parsed_data_list:
            parsed_data["from"] = msg.get("from")
            print("Parsed Data:", parsed_data)
            print("=" * 60)

        print("\n" + "=" * 80 + "\n")
        print(f"From: {msg.get('from', 'MISSING')}")

