from flask import Flask, send_from_directory, request
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
auth = HTTPBasicAuth()

# USERNAME + PASSWORD CONFIG
users = {
    "admin": generate_password_hash("U7nsXqa1mwb@ob")
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

# Where the logs are stored
LOGS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))

@app.after_request
def add_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    return response

@app.route("/")
@auth.login_required
def home():
    return """
    <html>
    <head>
        <title>GrayBotOps Logs</title>
    </head>
    <body style="text-align: center; font-family: Arial, sans-serif; margin-top: 50px;">
        <img src="/static/graybot_logo.png?v=1" alt="GrayBot Logo" style="width: 300px; margin-bottom: 20px;">
        <h1>GrayBotOps Logs Dashboard</h1>
        <p><a href="/download-log" style="font-size: 20px;">⬇️ Download Latest Log CSV</a></p>
    </body>
    </html>
    """

@app.route("/download-log")
@auth.login_required
def download_log():
    filename = "email_log.csv"
    file_path = os.path.join(LOGS_FOLDER, filename)

    if not os.path.exists(file_path):
        return "Log file not found.", 404

    print(f"📥 {auth.current_user()} downloaded the log.")
    return send_from_directory(LOGS_FOLDER, filename, as_attachment=True)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
