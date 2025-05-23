import json
import pymysql
from datetime import datetime
from dbcon import get_database_connection

def fetch_logins():
    connection = None
    cursor = None
    try:
        connection = get_database_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        sql = "SELECT session_id, email, session_creation, session_expiry FROM logins"
        cursor.execute(sql)
        logins = cursor.fetchall()

        # Format datetime values as strings
        for login in logins:
            login["session_creation"] = login["session_creation"].strftime("%Y-%m-%d %H:%M:%S") if login["session_creation"] else None
            login["session_expiry"] = login["session_expiry"].strftime("%Y-%m-%d %H:%M:%S") if login["session_expiry"] else None

        return {"data": logins}

    except pymysql.MySQLError as e:
        return {"success": False, "error": str(e)}

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def application(environ, start_response):
    try:
        response = fetch_logins()
        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(response).encode("utf-8")]
    except Exception as e:
        start_response("500 Internal Server Error", [("Content-Type", "application/json")])
        return [json.dumps({"success": False, "error": str(e)}).encode("utf-8")]
