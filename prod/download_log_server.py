from flask import Flask, send_from_directory
import os

app = Flask(__name__)

# Where the logs are stored relative to this file
LOGS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))

@app.route("/")
def home():
    return """
    <h1>GrayBotOps Logs</h1>
    <p><a href="/download-log">Download Latest Log CSV</a></p>
    """

@app.route("/download-log")
def download_log():
    filename = "email_log.csv"
    file_path = os.path.join(LOGS_FOLDER, filename)

    if not os.path.exists(file_path):
        return "Log file not found.", 404

    return send_from_directory(LOGS_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Railway injects $PORT
    app.run(host="0.0.0.0", port=port)
