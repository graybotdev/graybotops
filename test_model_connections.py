# test_model_connections.py

from app.firework_client import run_firework_model
from app.openai_client import run_openai_model

def test_firework():
    prompt = "Say hello from Firework!"
    result = run_firework_model(prompt)
    if result:
        print(f"✅ Firework response: {result}")
    else:
        print("❌ Firework failed. Falling back triggered or no response.")

def test_openai():
    prompt = "Say hello from OpenAI!"
    result = run_openai_model(prompt)
    if result:
        print(f"✅ OpenAI response: {result}")
    else:
        print("❌ OpenAI failed.")

if __name__ == "__main__":
    print("Running Firework API Test...")
    test_firework()
    
    print("\nRunning OpenAI API Test...")
    test_openai()
