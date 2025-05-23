#!/usr/bin/env python3  # Use this for CGI scripts
import pymysql  # type: ignore
import logging
import hashlib
import os

# Configure logging
log_path = "/home/handel/public_html/cgi-bin/dbcon.log"  # Save logs in the correct directory
logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def get_database_connection():
    """Establish a connection to the MySQL database on PythonAnywhere."""
    try:
        # Get configuration from environment variables to keep things secure
        config = {
            "host": os.getenv("DB_HOST", "handel.mysql.pythonanywhere-services.com"),
            "user": os.getenv("DB_USER", "handel"),
            "password": os.getenv("DB_PASSWORD", "Teknix96"),
            "database": os.getenv("DB_NAME", "handel$countyproj")
        }

        logging.debug(f"Using PythonAnywhere DB config: {config['host']}")

        # Establish a database connection
        connection = pymysql.connect(
            host=config["host"],
            user=config["user"],
            password=config["password"],
            database=config["database"],
            cursorclass=pymysql.cursors.DictCursor
        )
        logging.info("Database connection established successfully.")

        return connection

    except pymysql.MySQLError as e:
        logging.error(f"Database connection failed: {e}")
        raise RuntimeError(f"Error connecting to the database: {e}")

    except Exception as ex:
        logging.error(f"Unexpected error: {ex}")
        raise RuntimeError(f"An unexpected error occurred: {ex}")

def hash_password(password):
    """Hash a password using SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()

