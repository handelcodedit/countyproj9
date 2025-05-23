#!/usr/bin/env python3
import os
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs
import requests
from dotenv import load_dotenv
from dbcon import get_database_connection

# Load .env from the same directory as this script
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

def log_debug(message):
    with open("/home/handel/mysite/debug.log", "a") as f:
        f.write(f"[DEBUG] {datetime.now(timezone.utc)} - {message}\n")

def forgot_password(user_email):
    try:
        log_debug("forgot_password() called")

        # Connect to the database
        conn = get_database_connection()
        cursor = conn.cursor()

        # Validate email in DB
        cursor.execute("SELECT email FROM users WHERE email = %s", (user_email,))
        result = cursor.fetchone()
        log_debug(f"Email lookup: {result}")
        if not result:
            return "Email not found."

        # Generate reset token + expiry in UTC
        reset_token = str(uuid.uuid4())
        reset_token_expiry = datetime.now(timezone.utc) + timedelta(hours=1)

        cursor.execute("""
            UPDATE users
            SET reset_token = %s, reset_token_expiry = %s
            WHERE email = %s
        """, (reset_token, reset_token_expiry, user_email))
        conn.commit()

        reset_link = f"https://handel.pythonanywhere.com/reset_password.html?token={reset_token}"

        # Email payload for Brevo API
        payload = {
            "sender": {"name": "K9UNIT System", "email": "tchomlee@gmail.com"},
            "to": [{"email": user_email}],
            "subject": "Password Reset Request",
            "htmlContent": f"""
                <p>You requested a password reset.</p>
                <p><a href="{reset_link}">Reset Password</a></p>
                <p>This link expires in 1 hour.</p>
            """
        }

        # Load API key and check it exists
        brevo_api_key = os.getenv("BREVO_API_KEY")
        if not brevo_api_key:
            log_debug("BREVO_API_KEY is missing or not loaded from .env")
            return "Internal Error: Missing API key."

       

        headers = {
            "api-key": brevo_api_key,
            "accept": "application/json",
            "content-type": "application/json"
        }

        # Send email via Brevo
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email",
            json=payload,
            headers=headers
        )

        log_debug(f"Email response: {response.status_code} - {response.text}")

        return "Password reset email sent." if response.status_code == 201 else f"Email failed: {response.status_code} - {response.text}"

    except Exception as e:
        log_debug(f"Exception: {e}")
        return f"Error: {e}"

    finally:
        cursor.close()
        conn.close()
        log_debug("DB connection closed")

def application(environ, start_response):
    try:
        log_debug("WSGI Triggered")

        method = environ.get("REQUEST_METHOD", "GET")
        query = environ.get("QUERY_STRING", "")
        log_debug(f"Method: {method}, Query: {query}")

        if method not in ("POST", "GET"):
            start_response("405 Method Not Allowed", [("Content-Type", "text/html")])
            return [b"<h1>405 Not Allowed</h1>"]

        if method == "POST":
            size = int(environ.get("CONTENT_LENGTH", 0)) if environ.get("CONTENT_LENGTH") else 0
            data = environ["wsgi.input"].read(size).decode("utf-8")
        else:
            data = query

        form = parse_qs(data)
        user_email = form.get("email", [""])[0].strip()

        if not user_email:
            start_response("200 OK", [("Content-Type", "text/html")])
            return [b"<h1>Error</h1><p>Email is required.</p>"]

        result = forgot_password(user_email)
        start_response("200 OK", [("Content-Type", "text/html")])
        return [f"<h1>Result</h1><p>{result}</p>".encode("utf-8")]

    except Exception as e:
        log_debug(f"WSGI Exception: {e}")
        start_response("500 Internal Server Error", [("Content-Type", "text/html")])
        return [f"<h1>Error</h1><p>{e}</p>".encode("utf-8")]
