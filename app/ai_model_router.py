# app/ai_model_router.py

from app.firework_client import run_firework_model
from app.openai_client import run_openai_model

def generate_response(prompt):
    """Route prompt intelligently: Firework first, fallback to OpenAI if needed."""
    firework_response = run_firework_model(prompt)
    if firework_response:
        return firework_response

    print("[GrayBot] Firework failed. Falling back to OpenAI...")
    openai_response = run_openai_model(prompt)
    if openai_response:
        return openai_response

    print("[GrayBot] Both Firework and OpenAI failed.")
    return None
