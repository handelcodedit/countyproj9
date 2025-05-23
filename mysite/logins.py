#!/usr/bin/env python3

import os
import pymysql
import uuid
from dbcon import get_database_connection
from hashlib import sha256
from http.cookies import SimpleCookie
from urllib.parse import parse_qs
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo  # Python 3.9+

# Nairobi timezone
NAIROBI_TZ = ZoneInfo("Africa/Nairobi")

def hash_password(password):
    return sha256(password.encode()).hexdigest()

def application(environ, start_response):
    """Handles user login requests via WSGI"""
    
    request_method = environ.get("REQUEST_METHOD", "GET")
    post_data = {}

    if request_method == "POST":
        try:
            content_length = int(environ.get("CONTENT_LENGTH", 0))
            post_data = parse_qs(environ["wsgi.input"].read(content_length).decode())
        except (ValueError, KeyError):
            post_data = {}

    email = post_data.get("email", [""])[0]
    password = post_data.get("password", [""])[0]

    if not email or not password:
        response_body = "<h2>Missing email or password. <a href='/login.html'>Try again</a></h2>"
        start_response("400 Bad Request", [("Content-Type", "text/html")])
        return [response_body.encode()]

    conn = get_database_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Use Nairobi time for consistency
    now = datetime.now(NAIROBI_TZ)
    current_time_str = now.strftime('%Y-%m-%d %H:%M:%S')

    # Delete expired sessions
    cursor.execute("DELETE FROM logins WHERE session_expiry < %s", (current_time_str,))
    conn.commit()

    # Validate user
    cursor.execute("SELECT id, password_hash, role FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and user["password_hash"] == hash_password(password):
        session_id = str(uuid.uuid4())
        session_expiry = now + timedelta(hours=1)

        # Insert login record
        cursor.execute("""
            INSERT INTO logins (session_id, email, session_creation, session_expiry)
            VALUES (%s, %s, %s, %s)
        """, (session_id, email, now.strftime('%Y-%m-%d %H:%M:%S'), session_expiry.strftime('%Y-%m-%d %H:%M:%S')))
        conn.commit()

        # Set session cookie
        cookie = SimpleCookie()
        cookie["session_id"] = session_id
        cookie["session_id"]["path"] = "/"
        cookie["session_id"]["expires"] = session_expiry.strftime("%a, %d-%b-%Y %H:%M:%S GMT")

        # Role-based redirection
        if user["role"] == "admin":
            redirect_url = "/adminhome.html"
        elif user["role"] in ["governor", "senator", "mca"]:
            redirect_url = "/govyhome.html"
        else:
            redirect_url = "/home.html"

        start_response("302 Found", [("Location", redirect_url), ("Set-Cookie", cookie.output(header=""))])
        return []

    else:
        response_body = "<h2>Invalid email or password. <a href='/login.html'>Try again</a></h2>"
        start_response("401 Unauthorized", [("Content-Type", "text/html")])
        return [response_body.encode()]

    # Cleanup
    cursor.close()
    conn.close()


# Optional CGI fallback test
if __name__ == "__main__":
    environ = os.environ
    def fake_start_response(status, headers):
        print("Status:", status)
        for header in headers:
            print(f"{header[0]}: {header[1]}")
        print()

    response = application(environ, fake_start_response)
    for part in response:
        print(part.decode("utf-8"))
