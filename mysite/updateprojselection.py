#!/usr/bin/env python3  # Use this for CGI scripts
import csv
from dbcon import get_database_connection

def upload_csv_to_database(csv_file, table_name):
    # Connect to MySQL
    connection = get_database_connection()
    cursor = connection.cursor()

    try:
        # Open the CSV file
        with open(csv_file, 'r') as file:
            csv_reader = csv.reader(file)

            # Iterate over each row in the CSV file
            for row in csv_reader:
                # Construct the SQL INSERT statement dynamically based on the number of columns
                placeholders = ', '.join(['%s'] * len(row))
                sql = f"INSERT INTO {table_name} VALUES ({placeholders})"

                # Execute the SQL statement with the values from the CSV row
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
    csv_file ="C:/Apache24/htdocs/countyproj9/cgi-bin/projselection.csv"
    table_name = "proj_selection"

    # Call the function to upload CSV data to the database
    upload_csv_to_database(csv_file, table_name)