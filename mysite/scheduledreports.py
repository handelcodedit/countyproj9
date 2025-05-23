import json
import pymysql
from urllib.parse import parse_qs
from pymysql.cursors import DictCursor
from datetime import datetime
from dbcon import get_database_connection

def convert_to_date(date_str):
    """Convert a date string to a date object."""
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

def fetch_user_location(session_id):
    """Fetch county_id and ward_id for a user based on session_id."""
    try:
        with get_database_connection() as connection:
            cursor = connection.cursor(DictCursor)

            cursor.execute("SELECT email FROM logins WHERE session_id = %s", (session_id,))
            session_data = cursor.fetchone()
            if not session_data:
                return None

            cursor.execute("SELECT county_id, ward_id FROM users WHERE email = %s", (session_data['email'],))
            return cursor.fetchone()
    except pymysql.MySQLError:
        return None

def fetch_scheduled_reports(county_id, ward_id):
    """Fetch and structure project data grouped by status and period."""
    try:
        with get_database_connection() as connection:
            cursor = connection.cursor(DictCursor)

            cursor.execute("""
                SELECT project_name, status,
                       COALESCE(proposed_date, commence_date, completion_date) AS project_date
                FROM project_list
                WHERE county_id = %s AND ward_id = %s
            """, (county_id, ward_id))

            projects = cursor.fetchall()

            report = {}
            for project in projects:
                status = project["status"]
                date = project["project_date"].strftime('%B %Y') if project["project_date"] else "Unknown Period"

                if status not in report:
                    report[status] = {}
                if date not in report[status]:
                    report[status][date] = []

                report[status][date].append({
                    "project_name": project["project_name"],
                    "date": project["project_date"].strftime('%Y-%m-%d') if project["project_date"] else "N/A"
                })

            return report

    except pymysql.MySQLError:
        return {"error": "Database error"}


def application(environ, start_response):
    """WSGI application handler for scheduled reports."""
    try:
        method = environ["REQUEST_METHOD"]
        if method == "POST":
            content_length = int(environ.get("CONTENT_LENGTH", 0))
            post_data = parse_qs(environ["wsgi.input"].read(content_length).decode())
        else:
            post_data = parse_qs(environ.get("QUERY_STRING", ""))

        session_id = post_data.get("session_id", [None])[0]
        headers = [("Content-Type", "application/json"), ("Access-Control-Allow-Origin", "*")]

        if not session_id:
            response = json.dumps({"error": "Session ID is missing"}).encode()
            start_response("400 Bad Request", headers)
            return [response]

        user_location = fetch_user_location(session_id)
        if not user_location:
            response = json.dumps({"error": "User location not found"}).encode()
            start_response("404 Not Found", headers)
            return [response]

        county_id = user_location["county_id"]
        ward_id = user_location["ward_id"]
        report = fetch_scheduled_reports(county_id, ward_id)

        status = "200 OK" if "error" not in report else "500 Internal Server Error"
        start_response(status, headers)
        return [json.dumps(report).encode()]

    except Exception as e:
        error = json.dumps({"error": f"Unhandled exception: {str(e)}"}).encode()
        start_response("500 Internal Server Error", [("Content-Type", "application/json")])
        return [error]
