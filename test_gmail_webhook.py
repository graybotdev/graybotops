# test_gmail_webhook.py

import json
import base64
import requests

# 1) Create a fake “historyId” payload
payload = {"historyId": "123"}  

# 2) Base64‑encode it exactly how Pub/Sub will
data_b64 = base64.urlsafe_b64encode(
    json.dumps(payload).encode("utf-8")
).decode("utf-8")

# 3) Build the full body that your Flask app expects
body = {"message": {"data": data_b64}}

# 4) Send the POST to your local listener
url = "http://localhost:5000/gmail_webhook"
resp = requests.post(url, json=body)

print("Status:", resp.status_code)
print("Response:", resp.text)
