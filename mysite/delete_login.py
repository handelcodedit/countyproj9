#!/usr/bin/env python3

import pymysql
import os
from dbcon import get_database_connection
from http.cookies import SimpleCookie
from urllib.parse import parse_qs
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+

# Nairobi timezone
NAIROBI_TZ = ZoneInfo("Africa/Nairobi")
LOG_FILE = "error_log.txt"

def log_error(message):
    """Log errors to a file with timestamp in Nairobi timezone."""
    with open(LOG_FILE, "a") as error_file:
        timestamp = datetime.now(NAIROBI_TZ).strftime("%Y-%m-%d %H:%M:%S")
        error_file.write(f"{timestamp}: {message}\n")

def delete_login(session_id):
    """Delete a login session from the database."""
    connection = None
    cursor = None
    try:
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM logins WHERE session_id = %s", (session_id,))
        connection.commit()
        return True
    except pymysql.MySQLError as e:
        log_error(f"Database Error: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def application(environ, start_response):
    try:
        # Get cookies from headers
        cookie = SimpleCookie(environ.get('HTTP_COOKIE', ''))
        admin_session = cookie.get('session_id').value if cookie.get('session_id') else None

        if not admin_session:
            raise ValueError("Admin session ID is missing.")

        # Get POST or GET data depending on method
        request_method = environ.get("REQUEST_METHOD", "GET")
        form_data = {}

        if request_method == "POST":
            try:
                content_length = int(environ.get("CONTENT_LENGTH", 0))
                form_data = parse_qs(environ["wsgi.input"].read(content_length).decode())
            except (ValueError, KeyError):
                form_data = {}
        elif request_method == "GET":
            form_data = parse_qs(environ.get("QUERY_STRING", ""))

        session_id_to_delete = form_data.get("session_id", [""])[0]

        if not session_id_to_delete:
            raise ValueError("Session ID to delete is missing.")

        # Attempt to delete session
        if delete_login(session_id_to_delete):
            start_response("200 OK", [("Content-Type", "text/html")])
            return [b"<html><body><h2>Login session deletion successful!</h2></body></html>"]
        else:
            start_response("500 Internal Server Error", [("Content-Type", "text/html")])
            return [b"<html><body><h2>Failed to delete login session. Check logs for details.</h2></body></html>"]

    except Exception as e:
        log_error(f"Unhandled Error: {e}")
        start_response("500 Internal Server Error", [("Content-Type", "text/html")])
        return [f"<html><body><h2>Error: {e}</h2></body></html>".encode()]
