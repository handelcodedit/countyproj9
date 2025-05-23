#!/usr/bin/env python3  # Use this for CGI scripts

import cgi
import cgitb
import pymysql
import os
import json
from dbcon import get_database_connection
from http import cookies
from datetime import datetime

# Enable debugging
cgitb.enable()

def log_error(message):
    """Log errors to a file."""
    with open("error_log.txt", "a") as error_file:
        error_file.write(f"{datetime.now()}: {message}\n")

def update_user(data):
    """Update user details in the database."""
    connection = None
    cursor = None
    try:
        connection = get_database_connection()
        cursor = connection.cursor()

        # Check if user exists before updating
        cursor.execute("SELECT id FROM users WHERE id = %s", (data["id"],))
        user_exists = cursor.fetchone()

        if not user_exists:
            return {"success": False, "error": "User not found."}

        # Perform update
        sql = """UPDATE users SET 
                    username = %s, 
                    email = %s, 
                    fname = %s, 
                    lname = %s, 
                    gender = %s, 
                    dob = %s, 
                    role = %s, 
                    county_id = %s, 
                    ward_id = %s, 
                    address = %s, 
                    achievements = %s, 
                    occupation = %s, 
                    marital_status = %s, 
                    education_level = %s
                 WHERE id = %s"""

        values = (
            data["username"], data["email"], data["fname"], data["lname"], data["gender"], 
            data["dob"], data["role"], data["county_id"], data["ward"], data["address"], 
            data["achievements"], data["occupation"], data["marital_status"], 
            data["education_level"], data["id"]
        )

        cursor.execute(sql, values)
        connection.commit()
        
        return {"success": True, "message": "User updated successfully."}
    
    except pymysql.MySQLError as e:
        log_error(f"Database Error: {e}")
        return {"success": False, "error": str(e)}
    
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Parse form data
form = cgi.FieldStorage()

try:
    # Extract session_id from cookies
    cookie = cookies.SimpleCookie(os.environ.get('HTTP_COOKIE'))
    session_id = cookie.get('session_id').value if cookie.get('session_id') else None

    if not session_id:
        raise ValueError("Session ID is missing.")

    # Retrieve form values
    user_data = {
        "id": form.getvalue("id"),
        "username": form.getvalue("username"),
        "email": form.getvalue("email"),  # Added email field
        "fname": form.getvalue("fname"),
        "lname": form.getvalue("lname"),
        "gender": form.getvalue("gender"),
        "dob": form.getvalue("dob"),
        "role": form.getvalue("role"),
        "county_id": form.getvalue("county_id"),
        "ward": form.getvalue("ward"),
        "address": form.getvalue("address"),
        "achievements": form.getvalue("achievements"),
        "occupation": form.getvalue("occupation"),
        "marital_status": form.getvalue("marital_status"),
        "education_level": form.getvalue("education_level"),
    }

    # Update user in database
    response = update_user(user_data)

    # Return JSON response
    print("Content-Type: application/json\n")
    print(json.dumps(response))

except Exception as e:
    log_error(f"Unhandled Error: {e}")
    print("Content-Type: application/json\n")
    print(json.dumps({"success": False, "error": str(e)}))
