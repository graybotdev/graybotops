# app/firework_client.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

FIREWORK_API_KEY = os.getenv("FIREWORK_API_KEY")
FIREWORK_URL = "https://api.firework.ai/v1/generate"  # Replace with actual endpoint if different

HEADERS = {
    "Authorization": f"Bearer {FIREWORK_API_KEY}",
    "Content-Type": "application/json"
}

def run_firework_model(prompt, model="accounts/firework/models/firefunction-v1", temperature=0.3, max_tokens=300):
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        response = requests.post(FIREWORK_URL, json=payload, headers=HEADERS)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[Firework ERROR] {e}")
        return None
