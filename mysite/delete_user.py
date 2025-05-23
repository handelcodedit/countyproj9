import pymysql
from dbcon import get_database_connection
from http import cookies
from urllib.parse import parse_qs
from datetime import datetime

def log_error(message):
    """Log errors to a file."""
    with open("/home/yourusername/error_log.txt", "a") as error_file:  # Adjust path for your PythonAnywhere home dir
        error_file.write(f"{datetime.now()}: {message}\n")

def delete_user(user_id):
    """Delete a user from the database."""
    connection = None
    cursor = None
    try:
        connection = get_database_connection()
        cursor = connection.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
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
        # Parse POST data
        try:
            request_body_size = int(environ.get('CONTENT_LENGTH', 0))
        except (ValueError):
            request_body_size = 0

        request_body = environ['wsgi.input'].read(request_body_size).decode('utf-8')
        post_data = parse_qs(request_body)
        user_id = post_data.get('id', [None])[0]

        # Parse cookies
        cookie = cookies.SimpleCookie(environ.get('HTTP_COOKIE', ''))
        session_id = cookie.get('session_id').value if cookie.get('session_id') else None

        if not session_id:
            raise ValueError("Session ID is missing.")

        if not user_id:
            raise ValueError("User ID is missing.")

        if delete_user(user_id):
            start_response("200 OK", [('Content-Type', 'text/html')])
            return [b"<html><body><h2>User deletion successful!</h2></body></html>"]
        else:
            start_response("500 Internal Server Error", [('Content-Type', 'text/html')])
            return [b"<html><body><h2>User deletion failed. Check logs for details.</h2></body></html>"]

    except Exception as e:
        log_error(f"Unhandled Error: {e}")
        start_response("500 Internal Server Error", [('Content-Type', 'text/html')])
        return [f"<html><body><h2>Error: {str(e)}</h2></body></html>".encode("utf-8")]
