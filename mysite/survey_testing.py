import json
import pymysql
from urllib.parse import parse_qs
from dbcon import get_database_connection

def get_projects(session_id):
    """
    Retrieve projects grouped by status for a given session_id.
    """
    connection = None
    cursor = None
    results = {
        "active_projects": [],
        "closed_projects": [],
        "pipeline_projects": [],
        "dropped_projects": []
    }

    try:
        connection = get_database_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # Validate session ID and retrieve email
        cursor.execute("SELECT email FROM logins WHERE session_id = %s", (session_id,))
        email_result = cursor.fetchone()
        if not email_result:
            return {"error": "Invalid session ID"}

        email = email_result["email"]

        # Get ward_id
        cursor.execute("SELECT ward_id FROM users WHERE email = %s", (email,))
        ward_result = cursor.fetchone()
        if not ward_result:
            return {"error": "No ward associated with this email"}

        ward_id = ward_result["ward_id"]

        # Fetch project names grouped by status
        status_map = {
            "Active": "active_projects",
            "Closed": "closed_projects",
            "Pipeline": "pipeline_projects",
            "Dropped": "dropped_projects"
        }

        for db_status, key in status_map.items():
            cursor.execute(
                "SELECT project_name FROM project_list WHERE ward_id = %s AND status = %s",
                (ward_id, db_status)
            )
            projects = cursor.fetchall()
            results[key] = [project["project_name"] for project in projects]

        return results

    except pymysql.MySQLError as e:
        return {"error": f"MySQL Error: {str(e)}"}
    except Exception as ex:
        return {"error": f"Unexpected Error: {str(ex)}"}
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def application(environ, start_response):
    """WSGI application entry point."""
    try:
        if environ["REQUEST_METHOD"] == "POST":
            request_body_size = int(environ.get("CONTENT_LENGTH", 0))
            request_body = environ["wsgi.input"].read(request_body_size).decode()
            post_data = parse_qs(request_body)
        else:
            post_data = parse_qs(environ.get("QUERY_STRING", ""))

        session_id = post_data.get("session_id", [None])[0]

        if not session_id:
            response_data = {"error": "Missing session_id"}
            status = "400 Bad Request"
        else:
            response_data = get_projects(session_id)
            status = "200 OK" if "error" not in response_data else "400 Bad Request"

    except Exception as ex:
        response_data = {"error": f"Unhandled exception: {str(ex)}"}
        status = "500 Internal Server Error"

    response_body = json.dumps(response_data).encode("utf-8")
    headers = [
        ("Content-Type", "application/json; charset=utf-8"),
        ("Content-Length", str(len(response_body)))
    ]

    start_response(status, headers)
    return [response_body]
