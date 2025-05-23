#!/usr/bin/env python3  # Use this for CGI scripts
import mysql.connector
import hashlib
import logging

# Configure logging
logging.basicConfig(
    filename="update_password.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def hash_password(password):
    """Hashes a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

def update_mysql_password(user, plaintext_password):
    """Updates the MySQL user's password with a hashed password."""
    try:
        # Connect as root or an admin user
        connection = mysql.connector.connect(
            host="localhost",
            user="root",  # Use root or a privileged admin account
            password="root"  # Replace with the root password
        )
        cursor = connection.cursor()

        # Hash the password
        hashed_password = hash_password(plaintext_password)
        logging.debug(f"Hashed password for user {user}: {hashed_password}")

        # Update the MySQL user's password
        query = f"ALTER USER '{user}'@'localhost' IDENTIFIED BY '{plaintext_password}';"
        cursor.execute(query)
        connection.commit()

        logging.info(f"Updated password for MySQL user '{user}'.")
        print(f"Password for MySQL user '{user}' updated successfully.")

        cursor.close()
        connection.close()

    except mysql.connector.Error as e:
        logging.error(f"Error updating MySQL password: {e}")
        raise RuntimeError(f"Failed to update MySQL user password: {e}")

if __name__ == "__main__":
    update_mysql_password("countyadmin", "gakuru")
