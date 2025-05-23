#!/usr/bin/env python3

import pymysql
import json
from dbcon import get_database_connection
from urllib.parse import parse_qs
from datetime import datetime, date
from decimal import Decimal

def serialize_result(projects):
    """Convert datetime, date, and decimal fields for JSON serialization"""
    for project in projects:
        for key, value in project.items():
            if isinstance(value, datetime):
                project[key] = value.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(value, date):
                project[key] = value.strftime("%Y-%m-%d")
            elif isinstance(value, Decimal):
                project[key] = float(value)
    return projects

def fetch_projects(form_data):
    """Fetch paginated and searchable project records for DataTables"""
    search_value = form_data.get("search[value]", [""])[0].strip()
    start = int(form_data.get("start", [0])[0])
    length = int(form_data.get("length", [10])[0])
    draw = int(form_data.get("draw", [1])[0])

    connection = None
    cursor = None

    try:
        connection = get_database_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        cursor.execute("SELECT COUNT(*) as total FROM project_list")
        total_records = cursor.fetchone()["total"]

        where_clause = ""
        if search_value:
            like = f"%{search_value}%"
            where_clause = """
                WHERE proposed_project_id LIKE %s OR
                      ward_id LIKE %s OR
                      proposed_date LIKE %s OR
                      project_type LIKE %s OR
                      project_name LIKE %s OR
                      county_id LIKE %s OR
                      budget_estimate LIKE %s OR
                      total_cost LIKE %s OR
                      commence_date LIKE %s OR
                      completion_date LIKE %s OR
                      status LIKE %s OR
                      period LIKE %s OR
                      contractor LIKE %s
            """
            like_values = [like] * 13
        else:
            like_values = []

        # Count filtered records
        cursor.execute(f"SELECT COUNT(*) as filtered FROM project_list {where_clause}", like_values)
        filtered_records = cursor.fetchone()["filtered"]

        # Get data
        paginated_query = f"SELECT * FROM project_list {where_clause} LIMIT %s, %s"
        cursor.execute(paginated_query, like_values + [start, length])
        projects = serialize_result(cursor.fetchall())

        return {
            "draw": draw,
            "recordsTotal": total_records,
            "recordsFiltered": filtered_records,
            "data": projects
        }

    except pymysql.MySQLError as e:
        return {"error": str(e)}

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def application(environ, start_response):
    try:
        # Parse request body (POST) or query string (GET)
        request_method = environ.get("REQUEST_METHOD", "GET")
        if request_method == "POST":
            try:
                content_length = int(environ.get("CONTENT_LENGTH", 0))
                body = environ["wsgi.input"].read(content_length).decode()
                form_data = parse_qs(body)
            except Exception:
                form_data = {}
        else:
            form_data = parse_qs(environ.get("QUERY_STRING", ""))

        response = fetch_projects(form_data)
        response_body = json.dumps(response).encode()

        start_response("200 OK", [("Content-Type", "application/json")])
        return [response_body]

    except Exception as e:
        error_response = json.dumps({"error": str(e)}).encode()
        start_response("500 Internal Server Error", [("Content-Type", "application/json")])
        return [error_response]
