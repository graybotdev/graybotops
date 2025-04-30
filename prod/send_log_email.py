import smtplib
import os
from email.message import EmailMessage
from datetime import datetime

EMAIL_ADDRESS = os.environ.get("SMTP_EMAIL")
EMAIL_PASSWORD = os.environ.get("SMTP_PASSWORD")
RECIPIENT = os.environ.get("LOG_RECIPIENT")
LOG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs", "email_log.csv"))

def send_log_email():
    if not os.path.exists(LOG_FILE):
        print("❌ Log file not found. Email not sent.")
        return

    msg = EmailMessage()
    msg["Subject"] = f"GrayBotOps Daily Log – {datetime.utcnow().strftime('%Y-%m-%d')}"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = RECIPIENT
    msg.set_content("Attached is the latest GrayBotOps email reply log.")

    with open(LOG_FILE, "rb") as f:
        file_data = f.read()
        msg.add_attachment(file_data, maintype="application", subtype="octet-stream", filename="email_log.csv")

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
            print("✅ Log email sent successfully.")
    except Exception as e:
        print(f"🚨 Failed to send email: {e}")

if __name__ == "__main__":
    send_log_email()
