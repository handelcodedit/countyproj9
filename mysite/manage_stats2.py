#!/usr/bin/env python3

import pymysql
import json
from urllib.parse import parse_qs
from dbcon import get_database_connection
from datetime import datetime, date
from decimal import Decimal

def serialize_records(records):
    for record in records:
        for key, value in record.items():
            if isinstance(value, datetime):
                record[key] = value.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(value, date):
                record[key] = value.strftime("%Y-%m-%d")
            elif isinstance(value, Decimal):
                record[key] = float(value)
    return records

def fetch_stats2(form_data):
    try:
        start = int(form_data.get("start", ["0"])[0])
        length = int(form_data.get("length", ["10"])[0])
        draw = int(form_data.get("draw", ["1"])[0])
        search_value = form_data.get("search[value]", [""])[0].strip()

        connection = get_database_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        base_query = "SELECT * FROM stats2"
        count_query = "SELECT COUNT(*) as total FROM stats2"

        search_condition = ""
        search_values = []

        if search_value:
            search_condition = " WHERE county_id LIKE %s"
            search_values = [f"%{search_value}%"]
            base_query += search_condition
            count_query += search_condition

        # Get filtered record count
        cursor.execute(count_query, search_values)
        total_filtered = cursor.fetchone()["total"]

        # Add pagination
        base_query += " LIMIT %s, %s"
        cursor.execute(base_query, search_values + [start, length])
        records = cursor.fetchall()

        serialize_records(records)

        # Get total unfiltered record count
        cursor.execute("SELECT COUNT(*) as total FROM stats2")
        total_records = cursor.fetchone()["total"]

        return {
            "draw": draw,
            "recordsTotal": total_records,
            "recordsFiltered": total_filtered,
            "data": records
        }

    except pymysql.MySQLError as e:
        return {"error": str(e)}

    finally:
        try:
            cursor.close()
            connection.close()
        except:
            pass

def application(environ, start_response):
    try:
        if environ.get("REQUEST_METHOD") == "POST":
            length = int(environ.get("CONTENT_LENGTH", 0))
            raw_data = environ["wsgi.input"].read(length).decode()
            form_data = parse_qs(raw_data)
        else:
            form_data = parse_qs(environ.get("QUERY_STRING", ""))

        result = fetch_stats2(form_data)
        response_body = json.dumps(result).encode()

        start_response("200 OK", [("Content-Type", "application/json")])
        return [response_body]

    except Exception as e:
        error_response = json.dumps({"error": str(e)}).encode()
        start_response("500 Internal Server Error", [("Content-Type", "application/json")])
        return [error_response]
