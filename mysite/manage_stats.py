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

def fetch_stats(form_data):
    try:
        start = int(form_data.get("start", ["0"])[0])
        length = int(form_data.get("length", ["10"])[0])
        draw = int(form_data.get("draw", ["1"])[0])
        search_value = form_data.get("search[value]", [""])[0].strip()

        connection = get_database_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        # Columns to fetch
        columns = """
            ward_id, project_completion, completion_percentage, initiative, proposal_success, 
            project_awareness, effective_communication, impact_on_the_community, 
            public_participation, project_management, budget_allocation_awareness, 
            financial_management, infrastructure_development, sustainability, inclusivity, 
            impact_on_specific_demographics, total_score, county_id
        """

        base_query = f"SELECT {columns} FROM stats"
        count_query = "SELECT COUNT(*) as total FROM stats"

        search_columns = ["ward_id", "county_id"]
        search_condition = ""
        search_values = []

        if search_value:
            search_condition = " WHERE " + " OR ".join([f"{col} LIKE %s" for col in search_columns])
            like_pattern = f"%{search_value}%"
            search_values = [like_pattern] * len(search_columns)

        # Get filtered record count
        cursor.execute(count_query + search_condition, search_values)
        total_filtered = cursor.fetchone()["total"]

        # Get paginated results
        cursor.execute(f"{base_query}{search_condition} LIMIT %s, %s", search_values + [start, length])
        stats = cursor.fetchall()
        serialize_records(stats)

        # Get total record count (unfiltered)
        cursor.execute("SELECT COUNT(*) as total FROM stats")
        total_records = cursor.fetchone()["total"]

        return {
            "draw": draw,
            "recordsTotal": total_records,
            "recordsFiltered": total_filtered,
            "data": stats
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
        if environ.get("REQUEST_METHOD", "GET") == "POST":
            try:
                length = int(environ.get("CONTENT_LENGTH", 0))
                raw_data = environ["wsgi.input"].read(length).decode()
                form_data = parse_qs(raw_data)
            except:
                form_data = {}
        else:
            form_data = parse_qs(environ.get("QUERY_STRING", ""))

        result = fetch_stats(form_data)
        response_body = json.dumps(result).encode()

        start_response("200 OK", [("Content-Type", "application/json")])
        return [response_body]

    except Exception as e:
        error_body = json.dumps({"error": str(e)}).encode()
        start_response("500 Internal Server Error", [("Content-Type", "application/json")])
        return [error_body]
