from flask import Flask, send_from_directory, request, render_template
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import os
import pandas as pd
import plotly.graph_objs as go
from plotly.utils import PlotlyJSONEncoder
import json
from datetime import datetime, timedelta

app = Flask(__name__)
auth = HTTPBasicAuth()

# Auth setup
users = {
    "admin": generate_password_hash("U7nsXqa1mwb@ob")
}

@auth.verify_password
def verify_password(username, password):
    if username in users and check_password_hash(users.get(username), password):
        return username

LOGS_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "logs"))

@app.after_request
def add_security_headers(response):
    response.headers["X-Frame-Options"] = "DENY"
    return response

@app.route("/")
@auth.login_required
def home():
    # Load email log
    log_path = os.path.join(LOGS_FOLDER, "email_log.csv")
    if not os.path.exists(log_path):
        return "No log data yet."

    df = pd.read_csv(log_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    df['date'] = df['timestamp'].dt.date

    # Replies over last 7 days
    today = datetime.utcnow().date()
    last_7_days = df[df['date'] >= (today - timedelta(days=6))]
    reply_counts = last_7_days.groupby('date').size().reindex(
        [today - timedelta(days=i) for i in reversed(range(7))],
        fill_value=0
    )

    reply_fig = go.Figure(data=[
        go.Bar(
            x=[str(date) for date in reply_counts.index],
            y=reply_counts.values,
            marker=dict(color='royalblue')
        )
    ])
    reply_fig.update_layout(
        title="Replies Over the Last 7 Days",
        xaxis_title="Date",
        yaxis_title="Reply Count",
        template="plotly_white"
    )
    graph_json = json.dumps(reply_fig, cls=PlotlyJSONEncoder)

    # GPT vs Firework usage chart
    model_counts = df['model_used'].str.lower().value_counts().reindex(['gpt', 'firework'], fill_value=0)
    model_fig = go.Figure(data=[
        go.Pie(
            labels=model_counts.index.str.upper(),
            values=model_counts.values,
            hole=0.4,
            marker=dict(colors=['#636EFA', '#EF553B'])
        )
    ])
    model_fig.update_layout(
        title="Model Usage Breakdown (GPT vs Firework)",
        template="plotly_white"
    )
    model_graph_json = json.dumps(model_fig, cls=PlotlyJSONEncoder)

    return render_template("dashboard.html", graph_json=graph_json, model_graph_json=model_graph_json)

@app.route("/download-log")
@auth.login_required
def download_log():
    filename = "email_log.csv"
    file_path = os.path.join(LOGS_FOLDER, filename)
    if not os.path.exists(file_path):
        return "Log file not found.", 404
    print(f"📥 {auth.current_user()} downloaded the log.")
    return send_from_directory(LOGS_FOLDER, filename, as_attachment=True)
