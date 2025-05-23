#!/usr/bin/env python3
import pymysql.cursors
import json
import urllib.parse
from dbcon import get_database_connection

def fetch_wards(county_id):
    """Fetch ward names for the given county ID."""
    try:
        connection = get_database_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT ward_name FROM proj_selection WHERE county_id = %s", (county_id,))
        wards = cursor.fetchall()
        return json.dumps([{"ward_name": ward["ward_name"]} for ward in wards])
    except pymysql.MySQLError as err:
        return json.dumps({"error": "Database error", "details": str(err)})
    finally:
        if cursor: cursor.close()
        if connection: connection.close()

def application(environ, start_response):
    """WSGI-compatible function to handle requests."""
    try:
        if environ["REQUEST_METHOD"] == "POST":
            size = int(environ.get("CONTENT_LENGTH", "0"))
            post_data = environ["wsgi.input"].read(size).decode("utf-8")
            form = urllib.parse.parse_qs(post_data)
        else:
            query_string = environ.get("QUERY_STRING", "")
            form = urllib.parse.parse_qs(query_string)

        county_id = int(form.get("county_id", [1])[0])  # Default to 1 if not provided
        response_body = fetch_wards(county_id)

        start_response("200 OK", [("Content-Type", "application/json")])
        return [response_body.encode("utf-8")]

    except Exception as e:
        error_message = json.dumps({"error": "Server error", "details": str(e)})
        start_response("500 Internal Server Error", [("Content-Type", "application/json")])
        return [error_message.encode("utf-8")]
