# survey_submit.py (WSGI-Compatible)
import json
import pymysql
from datetime import datetime, timezone
import urllib.parse
from dbcon import get_database_connection

def parse_post_data(environ):
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        request_body_size = 0
    request_body = environ['wsgi.input'].read(request_body_size).decode('utf-8')
    return urllib.parse.parse_qs(request_body)

def get_value(form, key):
    return form.get(key, [""])[0].strip()

def get_user_info(cursor, session_id):
    cursor.execute("SELECT email FROM logins WHERE session_id = %s", (session_id,))
    email_result = cursor.fetchone()
    if not email_result:
        return None, None, "Session ID not found"
    email = email_result['email']
    cursor.execute("SELECT id, ward_id FROM users WHERE email = %s", (email,))
    user_info_result = cursor.fetchone()
    if not user_info_result:
        return None, None, "User not found"
    return user_info_result['id'], user_info_result['ward_id'], None

def get_project_id(cursor, project_name):
    if project_name:
        cursor.execute("SELECT proposed_project_id FROM project_list WHERE project_name = %s", (project_name,))
        result = cursor.fetchone()
        return result['proposed_project_id'] if result else None
    return None

def insert_survey_response(cursor, user_id, ward_id, evaluation_date, finished_pid, ongoing_pid, proposed_pid, dropped_pid, responses, suggestions):
    arguments = (
        user_id, ward_id, evaluation_date, finished_pid, ongoing_pid,
        proposed_pid, dropped_pid, responses['project_awareness'],
        responses['projects_communication_channels'], responses['project_impact'],
        responses['project_negative_effects'], responses['project_participation'],
        responses['public_input'], responses['project_completion_status'],
        responses['prioritize_project_completion'],
        responses['budget_allocation_awareness'], responses['financial_management'],
        responses['infrastructure_development'], responses['environmental_impact'],
        responses['project_planning'], responses['inclusivity_in_project_implementation'],
        responses['impact_on_specific_demographics'],
        responses['future_project_preferences'], suggestions
    )
    cursor.execute("""
        INSERT INTO evaluation (
            user_id, ward_id, evaluation_date, closed_pid, active_pid, 
            proposed_pid, dropped_pid, project_awareness, 
            projects_communication_channels, project_impact, 
            project_negative_effects, project_participation, 
            public_input, project_completion_status, 
            prioritize_project_completion, budget_allocation_awareness, 
            financial_management, infrastructure_development, 
            environmental_impact, project_planning, 
            inclusivity_in_project_implementation, 
            impact_on_specific_demographics, future_project_preferences, 
            suggestions
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
    """, arguments)

def application(environ, start_response):
    response = {"status": "error", "message": "Unknown error"}
    connection = None
    cursor = None

    try:
        if environ["REQUEST_METHOD"] != "POST":
            start_response("405 Method Not Allowed", [("Content-Type", "application/json")])
            return [json.dumps({"status": "error", "message": "Method not allowed"}).encode("utf-8")]

        form = parse_post_data(environ)
        session_id = get_value(form, 'session_id')
        finished_project = get_value(form, 'finished_project')
        ongoing_project = get_value(form, 'ongoing_project')
        proposed_project = get_value(form, 'proposed_project')
        dropped_project = get_value(form, 'dropped_project')
        suggestions = get_value(form, 'suggestions')

        questions = [
            'project_awareness', 'projects_communication_channels', 'project_impact',
            'project_negative_effects', 'project_participation', 'public_input',
            'project_completion_status', 'prioritize_project_completion',
            'budget_allocation_awareness', 'financial_management', 'infrastructure_development',
            'environmental_impact', 'project_planning', 'inclusivity_in_project_implementation',
            'impact_on_specific_demographics', 'future_project_preferences'
        ]
        responses = {q: get_value(form, q) for q in questions}

        connection = get_database_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        user_id, ward_id, error_message = get_user_info(cursor, session_id)

        if error_message:
            response = {"status": "error", "message": error_message}
        else:
            # Set evaluation date in UTC
            evaluation_date = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
            finished_pid = get_project_id(cursor, finished_project)
            ongoing_pid = get_project_id(cursor, ongoing_project)
            proposed_pid = get_project_id(cursor, proposed_project)
            dropped_pid = get_project_id(cursor, dropped_project)

            insert_survey_response(cursor, user_id, ward_id, evaluation_date, finished_pid, ongoing_pid, proposed_pid, dropped_pid, responses, suggestions)
            connection.commit()
            response = {"status": "success", "message": "Survey submitted successfully"}

        start_response("200 OK", [("Content-Type", "application/json")])
        return [json.dumps(response).encode("utf-8")]

    except pymysql.MySQLError as err:
        response = {"status": "error", "message": f"MySQL error: {str(err)}"}
        start_response("500 Internal Server Error", [("Content-Type", "application/json")])
        return [json.dumps(response).encode("utf-8")]

    except Exception as ex:
        response = {"status": "error", "message": f"Unexpected error: {str(ex)}"}
        start_response("500 Internal Server Error", [("Content-Type", "application/json")])
        return [json.dumps(response).encode("utf-8")]

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
