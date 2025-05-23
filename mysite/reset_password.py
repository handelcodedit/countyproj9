# reset_password.py (WSGI-compatible)
import urllib.parse
from dbcon import get_database_connection, hash_password
from datetime import datetime, timezone
import pymysql

def application(environ, start_response):
    try:
        if environ["REQUEST_METHOD"] == "POST":
            size = int(environ.get("CONTENT_LENGTH", "0"))
            post_data = environ["wsgi.input"].read(size).decode("utf-8")
            form = urllib.parse.parse_qs(post_data)

            token = form.get("token", [""])[0]
            new_password = form.get("new_password", [""])[0]
            confirm_password = form.get("confirm_password", [""])[0]

            if new_password != confirm_password:
                raise ValueError("Passwords do not match")

            connection = get_database_connection()
            cursor = connection.cursor(pymysql.cursors.DictCursor)
            cursor.execute("""
                SELECT * FROM users WHERE reset_token=%s AND reset_token_expiry > UTC_TIMESTAMP()
            """, (token,))
            user = cursor.fetchone()

            if not user:
                raise ValueError("Invalid or expired token.")

            hashed_pw = hash_password(new_password)
            cursor.execute("""
                UPDATE users SET password_hash=%s, reset_token=NULL, reset_token_expiry=NULL
                WHERE id=%s
            """, (hashed_pw, user["id"]))
            connection.commit()

            start_response("302 Found", [("Location", "/login.html")])
            return [b"Password reset successful. Redirecting to login."]

        else:
            start_response("405 Method Not Allowed", [("Content-Type", "text/plain")])
            return [b"Method Not Allowed"]

    except Exception as e:
        start_response("400 Bad Request", [("Content-Type", "text/plain")])
        return [str(e).encode("utf-8")]