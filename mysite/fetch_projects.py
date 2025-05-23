#!/usr/bin/env python3  # Use this for CGI scripts
import pymysql
from dbcon import get_database_connection

def get_projects_for_user(session_id):
    """Fetch and print projects for a user based on their session_id."""
    connection = None
    cursor = None
    try:
        # Step 1: Connect to the database
        connection = get_database_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        
        # Step 2: Retrieve the email using session_id from the logins table
        cursor.execute("SELECT email FROM logins WHERE session_id = %s", (session_id,))
        email_result = cursor.fetchone()
        if not email_result:
            print("Invalid session ID.")
            return
        
        email = email_result["email"]
        print(f"Authenticated email: {email}")  # For debugging or confirmation
        
        # Step 3: Fetch ward_id using the email
        cursor.execute("SELECT ward_id FROM users WHERE email = %s", (email,))
        ward = cursor.fetchone()
        if not ward:
            print("No ward associated with the given email.")
            return
        
        ward_id = ward["ward_id"]
        # Update statuses to match actual database values
        statuses = ["Active", "Closed","Pipeline","Dropped"]

        # Step 4: Fetch projects for each status
        for status in statuses:
            cursor.execute(
                "SELECT project_name FROM project_list WHERE ward_id = %s AND status = %s",
                (ward_id, status)
            )
            projects = cursor.fetchall()
            print(f"Projects under {status}:")
            if projects:
                for project in projects:
                    print(f"- {project['project_name']}")
            else:
                print("No projects found under this status.")
            print()  # Add spacing for readability

    except pymysql.MySQLError as e:
        print(f"Database error: {e}")
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Example usage
if __name__ == "__main__":
    session_id = "1736851006"  # Replace with the actual session_id
    get_projects_for_user(session_id)
