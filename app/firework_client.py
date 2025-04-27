# app/firework_client.py

import os
import requests
from dotenv import load_dotenv
from app.openai_client import run_openai_model  # <- Make sure this function exists

load_dotenv()

FIREWORK_API_KEY = os.getenv("FIREWORK_API_KEY")
FIREWORK_URL = "https://api.fireworks.ai/inference/v1/chat/completions"  # Correct endpoint

HEADERS = {
    "Authorization": f"Bearer {FIREWORK_API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def run_firework_model(prompt, model="accounts/fireworks/models/llama4-scout-instruct-basic", temperature=0.6, max_tokens=1024):
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": temperature,
        "max_tokens": max_tokens
    }

    try:
        response = requests.post(FIREWORK_URL, json=payload, headers=HEADERS, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"[Firework ERROR] {e} — Falling back to OpenAI.")
        # Fallback: use OpenAI automatically if Firework fails
        return run_openai_model(prompt)
