#!/usr/bin/env python3

import pymysql
import json
from urllib.parse import parse_qs
from dbcon import get_database_connection
from datetime import datetime, date
from decimal import Decimal

def serialize_evaluations(evaluations):
    for evaluation in evaluations:
        for key, value in evaluation.items():
            if isinstance(value, datetime):
                evaluation[key] = value.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(value, date):
                evaluation[key] = value.strftime("%Y-%m-%d")
            elif isinstance(value, Decimal):
                evaluation[key] = float(value)
    return evaluations

def fetch_evaluations(form_data):
    try:
        start = int(form_data.get("start", ["0"])[0])
        length = int(form_data.get("length", ["10"])[0])
        draw = int(form_data.get("draw", ["1"])[0])
        search_value = form_data.get("search[value]", [""])[0].strip()

        connection = get_database_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)

        base_query = "SELECT * FROM evaluation"
        count_query = "SELECT COUNT(*) as total FROM evaluation"

        search_columns = [
            "id", "user_id", "evaluation_date",
            "closed_pid", "active_pid", "proposed_pid",
            "dropped_pid", "ward_id"
        ]

        search_condition = ""
        search_values = []

        if search_value:
            search_condition = " WHERE " + " OR ".join([f"{col} LIKE %s" for col in search_columns])
            like_pattern = f"%{search_value}%"
            search_values = [like_pattern] * len(search_columns)

        # Get total filtered count
        cursor.execute(count_query + search_condition, search_values)
        total_filtered = cursor.fetchone()["total"]

        # Get paginated results
        cursor.execute(f"{base_query}{search_condition} LIMIT %s, %s", search_values + [start, length])
        evaluations = cursor.fetchall()
        serialize_evaluations(evaluations)

        # Get total count (without filtering)
        cursor.execute("SELECT COUNT(*) as total FROM evaluation")
        total_records = cursor.fetchone()["total"]

        return {
            "draw": draw,
            "recordsTotal": total_records,
            "recordsFiltered": total_filtered,
            "data": evaluations
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
        method = environ.get("REQUEST_METHOD", "GET")
        if method == "POST":
            try:
                content_length = int(environ.get("CONTENT_LENGTH", 0))
                body = environ["wsgi.input"].read(content_length).decode()
                form_data = parse_qs(body)
            except:
                form_data = {}
        else:
            form_data = parse_qs(environ.get("QUERY_STRING", ""))

        result = fetch_evaluations(form_data)
        response_body = json.dumps(result).encode()

        start_response("200 OK", [("Content-Type", "application/json")])
        return [response_body]

    except Exception as e:
        error_body = json.dumps({"error": str(e)}).encode()
        start_response("500 Internal Server Error", [("Content-Type", "application/json")])
        return [error_body]
