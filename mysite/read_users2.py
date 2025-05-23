#!/usr/bin/env python3  # Use this for CGI scripts
import cgi
import cgitb
import pymysql
import os
from dbcon import get_database_connection
from http import cookies
from datetime import datetime

# Enable debugging for CGI scripts
cgitb.enable()

def log_error(message):
    """Log errors to a file."""
    with open("error_log.txt", "a") as error_file:
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
        return None
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

    # Read users
    result = read_users()

    # Output the result
    print("Content-Type: text/html\n")
    if result:
        print("<html><body><h2>All Users</h2>")
        print("<table border='1'>")
        print("<tr><th>ID</th><th>First Name</th><th>Last Name</th><th>Email</th><th>Actions</th></tr>")
        for row in result:
            print("<tr>")
            print(f"<td>{row['id']}</td>")
            print(f"<td>{row['fname']}</td>")
            print(f"<td>{row['lname']}</td>")
            print(f"<td>{row['email']}</td>")
            print(f"<td><button type='button' onclick='showUpdateForm({row})'>Update</button> <button type='button' onclick='deleteUser({row['id']})'>Delete</button></td>")
            print("</tr>")
        print("</table></body></html>")
    else:
        print("<html><body><h2>No users found.</h2></body></html>")

except Exception as e:
    log_error(f"Unhandled Error: {e}")
    print("Content-Type: text/html\n")
    print(f"<html><body><h2>Error: {e}</h2></body></html>")