#!/usr/bin/env python3  # Use this for CGI scripts
import cgi
import cgitb
from dbcon import get_database_connection
from http.cookies import SimpleCookie
import time
import urllib.parse  # Correct module for parse_qs

cgitb.enable()

# Define the redirect URL
redirect_url = "https://handel.pythonanywhere.com/login.html"

def delete_expired_sessions(cursor):
    """Delete expired sessions from the database."""
    current_time = time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())
    cursor.execute("DELETE FROM logins WHERE session_expiry < %s", (current_time,))
    cursor.connection.commit()

def handle_logout(session_id):
    """Handles the session deletion process."""
    conn = get_database_connection()
    cursor = conn.cursor()

    # Delete expired sessions
    delete_expired_sessions(cursor)

    # Delete the session record from the logins table
    cursor.execute("DELETE FROM logins WHERE session_id = %s", (session_id,))
    conn.commit()

    # Clear the session cookie
    cookie = SimpleCookie()
    cookie["session_id"] = ""
    cookie["session_id"]["path"] = "/"
    cookie["session_id"]["expires"] = "Thu, 01 Jan 1970 00:00:00 GMT"

    cursor.close()
    conn.close()

    return cookie

def application(environ, start_response):
    """Handles logout via WSGI."""
    try:
        if environ["REQUEST_METHOD"] == "POST":
            size = int(environ.get("CONTENT_LENGTH", "0"))
            post_data = environ["wsgi.input"].read(size).decode("utf-8")
            form = urllib.parse.parse_qs(post_data)  # FIXED: Using the correct module
            session_id = form.get("session_id", [""])[0]
        else:
            query_string = environ.get("QUERY_STRING", "")
            form = urllib.parse.parse_qs(query_string)  # FIXED: Using the correct module
            session_id = form.get("session_id", [""])[0]

        if not session_id:
            start_response("302 Found", [("Location", redirect_url)])
            return [b"Redirecting..."]

        cookie = handle_logout(session_id)

        headers = [
            ("Content-Type", "text/html"),
            ("Set-Cookie", cookie.output(header="").strip()),
            ("Location", redirect_url)
        ]
        start_response("302 Found", headers)
        return [b"Logout successful"]

    except Exception as e:
        start_response("500 Internal Server Error", [("Content-Type", "text/html")])
        return [f"<h2>Server Error: {e}</h2>".encode("utf-8")]

