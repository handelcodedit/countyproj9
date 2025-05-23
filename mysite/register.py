#!/usr/bin/env python3
import pymysql
from dbcon import get_database_connection, hash_password
from datetime import datetime
import urllib.parse

# Define the redirect URL
redirect_url = "https://handel.pythonanywhere.com/login.html"

def log_error(message):
    """Log errors to a file."""
    with open("error_log.txt", "a") as error_file:
        error_file.write(f"{datetime.now()}: {message}\n")

def get_ward_id(ward_name):
    """Fetch ward ID based on the ward name."""
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
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def register_user(data):
    """Insert user data into the database after validation."""
    connection = None
    cursor = None
    try:
        required_fields = [
            "id", "fname", "lname", "gender", "dob", "address", "county_id",
            "ward_id", "role", "email", "phone", "password_hash", "username", "registration_date"
        ]
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: {field}")

        connection = get_database_connection()
        cursor = connection.cursor()
        query = """
            INSERT INTO users (
                id, fname, lname, gender, dob, address, county_id, ward_id, role,
                achievements, occupation, marital_status, education_level, email, phone,
                password_hash, username, registration_date
            ) VALUES (
                %(id)s, %(fname)s, %(lname)s, %(gender)s, %(dob)s, %(address)s,
                %(county_id)s, %(ward_id)s, %(role)s, %(achievements)s, %(occupation)s,
                %(marital_status)s, %(education_level)s, %(email)s, %(phone)s, %(password_hash)s,
                %(username)s, %(registration_date)s
            )
        """
        cursor.execute(query, data)
        connection.commit()
        return True

    except ValueError as e:
        log_error(f"Validation Error: {e}")
        return False
    except pymysql.MySQLError as e:
        log_error(f"Database Error: {e}")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def application(environ, start_response):
    """Handles user registration via WSGI."""
    try:
        if environ["REQUEST_METHOD"] == "POST":
            size = int(environ.get("CONTENT_LENGTH", "0"))
            post_data = environ["wsgi.input"].read(size).decode("utf-8")
            form = urllib.parse.parse_qs(post_data)
        else:
            query_string = environ.get("QUERY_STRING", "")
            form = urllib.parse.parse_qs(query_string)

        data = {
            "id": form.get("id", [""])[0],
            "fname": form.get("fname", [""])[0],
            "lname": form.get("lname", [""])[0],
            "gender": form.get("gender", [""])[0],
            "dob": form.get("dob", [""])[0],
            "address": form.get("address", [""])[0],
            "county_id": int(form.get("county_id", [0])[0]),
            "ward_id": get_ward_id(form.get("ward", [""])[0]),
            "role": form.get("role", [""])[0],
            "achievements": form.get("achievements", [""])[0],
            "occupation": form.get("occupation", [""])[0],
            "marital_status": form.get("marital_status", [""])[0],
            "education_level": form.get("education_level", [""])[0],
            "email": form.get("email", [""])[0],
            "phone": form.get("phone", [""])[0],
            "password_hash": hash_password(form.get("password", [""])[0]),
            "username": form.get("username", [""])[0],
            "registration_date": datetime.now().strftime("%Y-%m-%d"),
        }

        with open("form_data_log.txt", "a") as log_file:
            log_file.write(f"{datetime.now()}: Received data: {data}\n")

        if register_user(data):
            start_response("302 Found", [("Location", redirect_url)])
            return [b"Registration successful! Redirecting..."]
        else:
            start_response("200 OK", [("Content-Type", "text/html")])
            return [b"<html><body><h2>Registration failed. Check logs for details.</h2></body></html>"]

    except Exception as e:
        log_error(f"Unhandled Error: {e}")
        start_response("500 Internal Server Error", [("Content-Type", "text/html")])
        return [f"<html><body><h2>Error: {e}</h2></body></html>".encode("utf-8")]
