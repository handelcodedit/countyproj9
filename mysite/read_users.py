import pymysql
import json
from dbcon import get_database_connection
from http import cookies
from datetime import datetime
from urllib.parse import parse_qs

def log_error(message):
    """Log errors to a file."""
    with open("/home/yourusername/error_log.txt", "a") as error_file:  # adjust path
        error_file.write(f"{datetime.now()}: {message}\n")

def read_users():
    """Read all users from the database."""
    connection = None
    cursor = None
    try:
        connection = get_database_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM users")
        result = cursor.fetchall()
        return result
    except pymysql.MySQLError as e:
        log_error(f"Database Error: {e}")
        return []
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def application(environ, start_response):
    try:
        # Extract cookies
        raw_cookie = environ.get('HTTP_COOKIE', '')
        cookie = cookies.SimpleCookie(raw_cookie)
        session_id = cookie.get('session_id').value if cookie.get('session_id') else None

        if not session_id:
            raise ValueError("Session ID is missing.")

        users = read_users()

        headers = [('Content-Type', 'text/html; charset=utf-8')]
        start_response('200 OK', headers)

        html = []
        html.append("<table id='usersTable' class='display' style='width:100%'>")
        html.append("<thead><tr>")
        if users:
            for column in users[0].keys():
                html.append(f"<th>{column.replace('_', ' ').title()}</th>")
        html.append("<th>Actions</th></tr></thead><tbody>")

        for row in users:
            user_data = json.dumps(row).replace('"', '&quot;')
            html.append("<tr>")
            for value in row.values():
                html.append(f"<td>{value}</td>")
            html.append(f"<td><button class='update-btn' data-user='{user_data}'>Update</button> ")
            html.append(f"<button class='delete-btn' data-id='{row['id']}'>Delete</button></td></tr>")

        html.append("</tbody></table>")
        return ["".join(html).encode("utf-8")]

    except Exception as e:
        log_error(f"Unhandled Error: {e}")
        start_response('500 Internal Server Error', [('Content-Type', 'text/html')])
        return [f"<h2>Error: {str(e)}</h2>".encode('utf-8')]
