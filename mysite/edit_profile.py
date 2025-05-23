#!/usr/bin/env python3  # Use this for CGI scripts
import pymysql
import hashlib
import cgi
import cgitb
from dbcon import get_database_connection
from http import cookies
import os

# Enable debugging
cgitb.enable()

# Function to get ward ID from ward name
def get_ward_id(ward_name):
    try:
        with get_database_connection() as connection:
            with connection.cursor() as cursor:
                query = "SELECT ward_id FROM proj_selection WHERE ward_name = %s"
                cursor.execute(query, (ward_name,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                return None
    except pymysql.MySQLError as err:
        print(f"Error: {err}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Function to retrieve the password hash from the database using the email
def get_password_hash(session_email):
    try:
        with get_database_connection() as connection:
            with connection.cursor() as cursor:
                query = "SELECT password_hash FROM users WHERE email = %s"
                cursor.execute(query, (session_email,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                return None
    except pymysql.MySQLError as err:
        print(f"Error: {err}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Function to retrieve the email from the logins table using session_id
def get_session_email(session_id):
    try:
        with get_database_connection() as connection:
            with connection.cursor() as cursor:
                query = "SELECT email FROM logins WHERE session_id = %s"
                cursor.execute(query, (session_id,))
                result = cursor.fetchone()
                if result:
                    return result[0]
                return None
    except pymysql.MySQLError as err:
        print(f"Error: {err}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Function to update user information
def update_user(id, username, ward_name, fname, lname, gender, dob, role, county_id, address, achievements, occupation, marital_status, education_level, email):
    ward_id = get_ward_id(ward_name)
    if ward_id is None:
        print(f"Could not retrieve ward ID for ward_name: {ward_name}")
        return False

    try:
        with get_database_connection() as connection:
            with connection.cursor() as cursor:
                update_query = """
                UPDATE users 
                SET id=%s, username=%s, ward_id=%s, fname=%s, lname=%s, gender=%s, dob=%s, role=%s, county_id=%s, address=%s, achievements=%s, occupation=%s, marital_status=%s, education_level=%s, email=%s
                WHERE email=%s
                """
                cursor.execute(update_query, (id, username, ward_id, fname, lname, gender, dob, role, county_id, address, achievements, occupation, marital_status, education_level, email, email))
                connection.commit()
                return cursor.rowcount > 0
    except pymysql.MySQLError as err:
        print(f"Error: {err}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

# Function to verify if the provided password matches the stored hash
def verify_password(input_password, stored_hash):
    try:
        # Hash the input password
        input_hash = hashlib.sha256(input_password.encode()).hexdigest()
        return input_hash == stored_hash
    except Exception as e:
        print(f"Error in verify_password: {e}")
        return False

# Get form data
form = cgi.FieldStorage()

# Get form values
username = form.getvalue('username')
email = form.getvalue('email')
password = form.getvalue('password')
id = form.getvalue('id')
ward_name = form.getvalue('ward')
fname = form.getvalue('fname')
lname = form.getvalue('lname')
gender = form.getvalue('gender')
dob = form.getvalue('dob')
role = form.getvalue('role')
county_id = form.getvalue('county_id')
address = form.getvalue('address')
achievements = form.getvalue('achievements')
occupation = form.getvalue('occupation')
marital_status = form.getvalue('marital_status')
education_level = form.getvalue('education_level')

# Retrieve session ID from cookies
def get_user_id_from_cookie():
    try:
        cookie = cookies.SimpleCookie(os.environ.get("HTTP_COOKIE"))
        session_id = cookie.get("session_id").value
        return session_id
    except Exception as e:
        print(f"Error retrieving session_id: {e}")
        return None

session_id = get_user_id_from_cookie()
session_email = get_session_email(session_id)

# Debug output
print("Content-Type: text/html")
print()  # Empty line to end headers
print("<html><body>")
print(f"Email from Form: {email}<br>")
print(f"Entered Password: {password}<br>")
print(f"ID from Form: {id}<br>")
print(f"Ward Name: {ward_name}<br>")
print(f"First Name: {fname}<br>")
print(f"Last Name: {lname}<br>")
print(f"Session Email: {session_email}<br>")
print("</body></html>")

# Password verification process
if session_email and password:
    stored_hash = get_password_hash(session_email)
    if stored_hash and verify_password(password, stored_hash):
        success = update_user(id, username, ward_name, fname, lname, gender, dob, role, county_id, address, achievements, occupation, marital_status, education_level, email)
    else:
        print("Password verification failed.<br>")
        success = False
else:
    print("Session email or password is missing.<br>")
    success = False

if success:
    print("Status: 303 See Other")
    print("Location: http://localhost/html/editprofile.html?message=Profile%20updated%20successfully!")
    print()  # Empty line to end headers
else:
    print("Content-Type: text/html")
    print()  # Empty line to end headers
    print('<html><body>')
    print('Internal Server Error: Could not update profile. Please check your password and try again.')
    print('</body></html>')
