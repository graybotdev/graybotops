import openai
import json
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def build_prompt(parsed_data):
    return f"""
You are GrayBot, a professional logistics assistant. Respond to the following logistics update in a friendly, professional, and concise tone.

Parsed load info:
{json.dumps(parsed_data, indent=2)}
"""

def generate_reply(parsed_data):
    prompt = build_prompt(parsed_data)

    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",  # or "gpt-4"
        messages=[
            {"role": "system", "content": "You are a helpful logistics assistant replying to logistics updates."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=300
    )

    return response.choices[0].message.content.strip()
