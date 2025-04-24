# Use Python base image
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run your app
CMD ["python", "test/run_auto_reply_cycle.py"]
