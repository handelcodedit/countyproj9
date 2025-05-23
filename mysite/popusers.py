#!/usr/bin/env python3  # Use this for CGI scripts
import pymysql  # Changed to pymysql
from dbcon import get_database_connection
from datetime import datetime
import random
import cgitb

# Enable CGI error reporting
cgitb.enable()

def random_date():
    start_date = datetime(1970, 1, 1)
    end_date = datetime(1995, 12, 31)
    random_date = start_date + (end_date - start_date) * random.random()
    return random_date.strftime('%Y-%m-%d')

def random_email(fname, lname):
    email_provider = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
    number = random.randint(100, 999)
    return f"{fname.lower()}.{lname.lower()}{number}@{random.choice(email_provider)}"

def random_phone():
    return f"07{random.randint(0, 9)}{random.randint(1000000, 9999999)}"

def generate_username(fname, lname):
    return f"{fname.lower()}{lname.lower()}{random.randint(100, 999)}"

def generate_names():
    first_names = {
        "male": ["John", "Michael", "David", "James", "Robert", "William", "Joseph", "Thomas", "Charles", "Christopher"],
        "female": ["Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"]
    }

    last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]

    return first_names, last_names

def fetch_valid_county_ward():
    try:
        connection = get_database_connection()
        cursor = connection.cursor(cursor=pymysql.cursors.DictCursor)  # Use DictCursor to fetch results as dictionaries
        cursor.execute("SELECT county_id, ward_id FROM project_list WHERE status = 'Closed'")
        results = cursor.fetchall()

        if not results:
            print("No valid county_id and ward_id found in project_list.")
            return []

        # Convert dictionary rows into tuples
        valid_data = [(int(row['county_id']), int(row['ward_id'])) for row in results]

        return valid_data

    except pymysql.MySQLError as error:
        print(f"Database error fetching project_list data: {error}")
        return []
    finally:
        cursor.close()
        connection.close()



def generate_users_data(count):
    first_names, last_names = generate_names()
    valid_county_ward = fetch_valid_county_ward()

    if not valid_county_ward:
        print("No valid county_id and ward_id found.")
        return []

    roles = ['user']
    achievements = 'Order of the Burning Spear'
    occupations = ['teacher', 'doctor', 'engineer', 'driver', 'barber']
    marital_statuses = ['single', 'married']
    education_levels = ['undergraduate', 'postgraduate']
    current_date = datetime.now().strftime('%Y-%m-%d')

    users_data = []
    for _ in range(count):
        gender = random.choice(['male', 'female'])
        fname = random.choice(first_names[gender])
        lname = random.choice(last_names)
        dob = random_date()
        address = '20100'
        county_id, ward_id = map(int, random.choice(valid_county_ward))
        role = random.choice(roles)
        achievements_text = achievements
        occupation = random.choice(occupations)
        marital_status = random.choice(marital_statuses)
        education_level = random.choice(education_levels)
        email = random_email(fname, lname)
        phone = random_phone()
        username = generate_username(fname, lname)
        user_id = random.randint(10000000, 99999999)
        password_hash = None
        reset_token = None
        reset_token_expiry = None

        users_data.append((fname, lname, gender, dob, address, county_id, ward_id, role, achievements_text,
                           occupation, marital_status, education_level, email, phone, username, user_id, password_hash,
                           reset_token, reset_token_expiry, current_date))

    return users_data

def insert_users_data(users_data):
    try:
        connection = get_database_connection()
        cursor = connection.cursor()

        insert_query = """
            INSERT INTO users (fname, lname, gender, dob, address, county_id, ward_id, role, achievements,
                               occupation, marital_status, education_level, email, phone, username, id, password_hash,
                               reset_token, reset_token_expiry, registration_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)
        """
        cursor.executemany(insert_query, users_data)
        connection.commit()
        print(f"{len(users_data)} records inserted successfully into 'users' table.")

    except pymysql.MySQLError as error:  # Changed to pymysql error handling
        print(f"Error inserting data into 'users' table: {error}")

    finally:
        cursor.close()
        connection.close()

def main():
    total_records = 5000
    batch_size = 1000

    for i in range(0, total_records, batch_size):
        batch_end = min(i + batch_size, total_records)
        users_data = generate_users_data(batch_end - i)
        if users_data:
            insert_users_data(users_data)

if __name__ == "__main__":
    main()
