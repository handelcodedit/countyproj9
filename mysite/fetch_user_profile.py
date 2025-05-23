#!/usr/bin/env python3
import pymysql.cursors
import json
import urllib.parse
from dbcon import get_database_connection

def fetch_user_profile(session_id):
    """Retrieve user profile data from the users table using the provided session_id."""
    try:
        if not session_id:
            return json.dumps({"error": "No session_id provided."})

        # Establish database connection
        connection = get_database_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # Step 1: Fetch email from logins table using session_id
        cursor.execute("SELECT email FROM logins WHERE session_id = %s", (session_id,))
        session_data = cursor.fetchone()

        if not session_data or "email" not in session_data:
            return json.dumps({"error": "Invalid session_id. No matching email found."})

        email = session_data["email"]

        # Step 2: Fetch user profile from users table using email
        cursor.execute("""
            SELECT 
                id, fname, lname, gender, dob, address, county_id, ward_id, role, 
                achievements, occupation, marital_status, education_level, email, 
                username, registration_date
            FROM users 
            WHERE email = %s
        """, (email,))
        user_profile = cursor.fetchone()

        if not user_profile:
            return json.dumps({"error": "No user profile found for the provided email."})

        # Convert `None` values to "N/A"
        user_profile_cleaned = {key: (value if value is not None else "N/A") for key, value in user_profile.items()}

        return json.dumps(user_profile_cleaned, default=str)

    except pymysql.MySQLError as e:
        return json.dumps({"error": f"Database error: {e}"})
    except Exception as ex:
        return json.dumps({"error": f"Unexpected error: {ex}"})
    finally:
        try:
            cursor.close()
            connection.close()
        except Exception:
            pass

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

        session_id = form.get("session_id", [""])[0]  # Get session_id from form data

        response_body = fetch_user_profile(session_id)

        start_response("200 OK", [("Content-Type", "application/json")])
        return [response_body.encode("utf-8")]

    except Exception as e:
        error_message = json.dumps({"error": "Server error", "details": str(e)})
        start_response("500 Internal Server Error", [("Content-Type", "application/json")])
        return [error_message.encode("utf-8")]
