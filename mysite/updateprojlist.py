#!/usr/bin/env python3  # Use this for CGI scripts

import csv
from datetime import datetime
from dbcon import get_database_connection

def preprocess_date(value):
    """
    Preprocess a date value, converting it from various formats to YYYY-MM-DD format.
    Return None if the value is invalid, empty, or None.
    """
    if not value or value.strip() == "":
        return None  # Handle null or empty values

    # Try parsing with multiple formats
    date_formats = ["%m/%d/%y", "%B %d, %Y", "%Y-%m-%d"]  # Add more formats if needed
    for fmt in date_formats:
        try:
            return datetime.strptime(value.strip(), fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue  # Try the next format

    return None  # Return None for invalid dates

def upload_csv_to_project_list(csv_file, table_name):
    """
    Upload data from a CSV file to the project_list table in MySQL.
    """
    # Connect to MySQL
    connection = get_database_connection()
    cursor = connection.cursor()

    try:
        # Open the CSV file
        with open(csv_file, 'r') as file:
            csv_reader = csv.reader(file)

            # Skip the header row
            header = next(csv_reader)

            # Iterate over each row in the CSV file
            for row in csv_reader:
                # Preprocess date columns (assume indices match column order in CSV)
                row[2] = preprocess_date(row[2])  # proposed_date
                row[8] = preprocess_date(row[8])  # commence_date
                row[9] = preprocess_date(row[9])  # completion_date

                # Construct the SQL INSERT statement dynamically
                placeholders = ', '.join(['%s'] * len(row))
                sql = f"INSERT INTO {table_name} VALUES ({placeholders})"

                # Execute the SQL statement with the processed row data
                cursor.execute(sql, tuple(row))

        # Commit the transaction
        connection.commit()
        print("CSV data uploaded to database successfully!")
    except Exception as e:
        # Rollback the transaction in case of error
        connection.rollback()
        print("Error uploading CSV data to database:", e)
    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()

if __name__ == "__main__":
    # Specify the path to your CSV file and table name
    csv_file = "C:/Apache24/htdocs/countyproj9/cgi-bin/projlist.csv"
    table_name = "project_list"

    # Call the function to upload CSV data to the database
    upload_csv_to_project_list(csv_file, table_name)
