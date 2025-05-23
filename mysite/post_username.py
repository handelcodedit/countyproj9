#!/usr/bin/env python3  # Use this for CGI scripts
import cgi
import logging
from dbcon import get_database_connection

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('connection_log.txt', mode='w'),
        logging.StreamHandler()
    ]
)

def post_to_database(username: str):
    """Post the given username to the test_data table."""
    conn = None
    try:
        logging.info("Attempting to connect to the database using dbcon.py...")
        conn = get_database_connection()

        with conn.cursor() as cursor:
            # Create the table if it doesn't exist
            create_table_query = """
            CREATE TABLE IF NOT EXISTS test_data (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL
            );
            """
            cursor.execute(create_table_query)

            # Insert the username into the table
            insert_query = "INSERT INTO test_data (username) VALUES (%s);"
            cursor.execute(insert_query, (username,))
            conn.commit()

            logging.info(f"Username '{username}' successfully inserted into the test_data table.")

    except Exception as ex:
        logging.error(f"Error occurred: {ex}")
    finally:
        if conn:
            conn.close()
            logging.info("Connection closed.")

def handle_form_submission():
    """Handle the form submission and process the username."""
    form = cgi.FieldStorage()
    username = form.getvalue("username")  # Get the username from the form

    if username:
        post_to_database(username)
        print("Content-type: text/html\n")  # CGI header
        print(f"<html><body><h1>Username '{username}' successfully posted!</h1></body></html>")
    else:
        print("Content-type: text/html\n")  # CGI header
        print("<html><body><h1>No username entered. Please try again.</h1></body></html>")

if __name__ == "__main__":
    handle_form_submission()
