import time
import subprocess
from datetime import datetime
import sys
import os

# Path to venv python.exe
VENV_PYTHON = os.path.join("venv", "Scripts", "python.exe")  # Windows

DELAY_SECONDS = 300  # 5 minutes

print("🌀 GrayBot Auto-Reply Loop Started")

while True:
    print(f"\n⏰ [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running auto-reply cycle...")
    subprocess.run([VENV_PYTHON, "-m", "test.run_auto_reply_cycle"])
    print(f"✅ Cycle complete. Sleeping for {DELAY_SECONDS} seconds...\n")
    time.sleep(DELAY_SECONDS)
    print("🔄 Restarting auto-reply cycle...")  