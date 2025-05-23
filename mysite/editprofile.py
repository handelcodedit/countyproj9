#!/usr/bin/env python3
import pymysql
import json
import urllib.parse
from http import cookies
from datetime import datetime
from dbcon import get_database_connection, hash_password

def log_error(message):
    with open("error_log.txt", "a") as error_file:
        error_file.write(f"{datetime.now()}: {message}\n")

def get_ward_id(ward_name):
    try:
        connection = get_database_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT ward_id FROM proj_selection WHERE ward_name = %s", (ward_name,))
        result = cursor.fetchone()
        return result["ward_id"] if result else None
    except pymysql.MySQLError as e:
        log_error(f"Database Error in get_ward_id: {e}")
        return None
    finally:
        try: cursor.close()
        except: pass
        try: connection.close()
        except: pass

def update_user(email, data):
    try:
        required = ["fname", "lname", "gender", "dob", "address", "county_id", "ward_id",
                    "role", "email", "phone", "username"]
        for field in required:
            if not data.get(field): raise ValueError(f"Missing field: {field}")

        connection = get_database_connection()
        cursor = connection.cursor()
        query = """
            UPDATE users SET
                fname=%(fname)s, lname=%(lname)s, gender=%(gender)s, dob=%(dob)s,
                address=%(address)s, county_id=%(county_id)s, ward_id=%(ward_id)s,
                role=%(role)s, achievements=%(achievements)s, occupation=%(occupation)s,
                marital_status=%(marital_status)s, education_level=%(education_level)s,
                email=%(email)s, phone=%(phone)s, username=%(username)s
            WHERE email=%(email)s
        """
        cursor.execute(query, data)
        connection.commit()
        return True
    except (ValueError, pymysql.MySQLError) as e:
        log_error(f"Update Error: {e}")
        return False
    finally:
        try: cursor.close()
        except: pass
        try: connection.close()
        except: pass

def process_update_request(form_data, session_id):
    try:
        if not session_id:
            return json.dumps({"error": "Missing session ID."})

        connection = get_database_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT email FROM logins WHERE session_id = %s", (session_id,))
        login_record = cursor.fetchone()

        if not login_record:
            return json.dumps({"error": "Invalid session."})

        email = login_record["email"]

        # Password verification
        password = form_data.get("password", [""])[0]
        hashed_password = hash_password(password)

        cursor.execute("SELECT password_hash FROM users WHERE email = %s", (email,))
        user_record = cursor.fetchone()
        if not user_record or user_record["password_hash"] != hashed_password:
            return json.dumps({"error": "Incorrect password."})

        # Collect and validate update data
        data = {
            "fname": form_data.get("fname", [""])[0],
            "lname": form_data.get("lname", [""])[0],
            "gender": form_data.get("gender", [""])[0],
            "dob": form_data.get("dob", [""])[0],
            "address": form_data.get("address", [""])[0],
            "county_id": int(form_data.get("county_id", [0])[0]),
            "ward_id": get_ward_id(form_data.get("ward", [""])[0]),
            "role": form_data.get("role", [""])[0],
            "achievements": form_data.get("achievements", [""])[0],
            "occupation": form_data.get("occupation", [""])[0],
            "marital_status": form_data.get("marital_status", [""])[0],
            "education_level": form_data.get("education_level", [""])[0],
            "email": email,
            "phone": form_data.get("phone", [""])[0],
            "username": form_data.get("username", [""])[0],
        }

        with open("form_data_log.txt", "a") as log:
            log.write(f"{datetime.now()} | {data}\n")

        return json.dumps({"success": "Profile updated!"}) if update_user(email, data) else json.dumps({"error": "Update failed."})

    except Exception as e:
        log_error(f"Unhandled Error: {e}")
        return json.dumps({"error": str(e)})

def application(environ, start_response):
    try:
        # Parse session_id from cookie
        cookie = cookies.SimpleCookie(environ.get("HTTP_COOKIE", ""))
        session_id = cookie.get("session_id").value if "session_id" in cookie else None

        # Handle GET or POST data
        if environ["REQUEST_METHOD"] == "POST":
            size = int(environ.get("CONTENT_LENGTH", 0))
            post_data = environ["wsgi.input"].read(size).decode("utf-8")
            form_data = urllib.parse.parse_qs(post_data)
        else:
            form_data = urllib.parse.parse_qs(environ.get("QUERY_STRING", ""))

        # Process update
        response = process_update_request(form_data, session_id)

        start_response("200 OK", [("Content-Type", "application/json")])
        return [response.encode("utf-8")]

    except Exception as e:
        log_error(f"WSGI Error: {e}")
        error_msg = json.dumps({"error": "Server error", "details": str(e)})
        start_response("500 Internal Server Error", [("Content-Type", "application/json")])
        return [error_msg.encode("utf-8")]
