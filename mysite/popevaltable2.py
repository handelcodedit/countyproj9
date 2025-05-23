#!/usr/bin/env python3  # Use this for CGI scripts
import pymysql
from dbcon import get_database_connection
from datetime import datetime
import random
import traceback
import json
import sys

def fetch_project_id(ward_id, status):
    """Fetch a single project_id from project_list based on ward and status."""
    try:
        connection = get_database_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)  # Ensure result is a dictionary
        cursor.execute(
            "SELECT proposed_project_id FROM project_list WHERE ward_id = %s AND status = %s LIMIT 1",
            (ward_id, status)
        )
        result = cursor.fetchone()
        cursor.close()
        connection.close()

        if result:
            project_id = result['proposed_project_id']
            print(f"✅ Found {status} project for ward_id {ward_id}: {project_id}")
            return project_id
        else:
            print(f"⚠️ No {status} project found for ward_id {ward_id}")
            return None
    except pymysql.MySQLError as error:
        print(f"❌ Database error fetching {status} project: {error}")
        return None

def fetch_users():
    """Fetch all users and their associated ward IDs from the database."""
    try:
        connection = get_database_connection()
        cursor = connection.cursor(pymysql.cursors.DictCursor)
        query = "SELECT id, ward_id FROM users"  # Removed TEST_MODE limit
        cursor.execute(query)
        users = cursor.fetchall()
        cursor.close()
        connection.close()
        
        for user in users:
            print(f"Fetched user: {user}")
        
        return users
    except pymysql.MySQLError as error:
        print(f"❌ Error fetching users: {error}")
        return []

def insert_survey_response(cursor, user_id, ward_id, evaluation_date, closed_pid, active_pid, proposed_pid, dropped_pid, responses, suggestions):
    """Insert evaluation data into the database."""
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
    """, (
        user_id, ward_id, evaluation_date, closed_pid, active_pid, 
        proposed_pid, dropped_pid, responses['project_awareness'],
        responses['projects_communication_channels'], responses['project_impact'],
        responses['project_negative_effects'], responses['project_participation'],
        responses['public_input'], responses['project_completion_status'],
        responses['prioritize_project_completion'], responses['budget_allocation_awareness'],
        responses['financial_management'], responses['infrastructure_development'],
        responses['environmental_impact'], responses['project_planning'],
        responses['inclusivity_in_project_implementation'],
        responses['impact_on_specific_demographics'],
        responses['future_project_preferences'], suggestions
    ))

def main():
    """Main function to process evaluations."""
    choices = {
        'project_awareness': ["Very informed", "Somewhat informed", "Not informed"],
        'projects_communication_channels': ["Yes", "No"],
        'project_impact': ["Significant impact", "Moderate impact", "No impact"],
        'project_negative_effects': ["Yes", "No"],
        'project_participation': ["Yes", "No"],
        'public_input': ["A lot", "Some", "None"],
        'project_completion_status': ["Always", "Sometimes", "Never"],
        'prioritize_project_completion': ["Yes", "No"],
        'budget_allocation_awareness': ["Yes", "No"],
        'financial_management': ["Excellent", "Good", "Poor"],
        'infrastructure_development': ["Satisfactory", "Needs Improvement", "Unsatisfactory"],
        'environmental_impact': ["Positive", "Negative", "No Impact"],
        'project_planning': ["Very Effective", "Moderately Effective", "Not Effective"],
        'inclusivity_in_project_implementation': ["Yes", "No"],
        'impact_on_specific_demographics': ["Yes", "No"],
        'future_project_preferences': ["Infrastructure", "Healthcare", "Education", "Environment"],
    }
    
    suggestions_list = [
        "Improve road infrastructure", 
        "Increase healthcare funding", 
        "Enhance educational facilities", 
        "Environmental conservation projects", 
        "No suggestions"
    ]

    users = fetch_users()
    if not users:
        print("No users found")
        return

    try:
        connection = get_database_connection()
        cursor = connection.cursor()

        for user in users:
            user_id = user['id']
            ward_id = user['ward_id']

            print(f"🔄 Processing user_id: {user_id}, ward_id: {ward_id}")

            closed_pid = fetch_project_id(ward_id, 'closed')
            active_pid = fetch_project_id(ward_id, 'active')
            proposed_pid = fetch_project_id(ward_id, 'proposed')
            dropped_pid = fetch_project_id(ward_id, 'dropped')

            evaluation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            responses = {question: random.choice(choices[question]) for question in choices}
            suggestions = random.choice(suggestions_list)

            print(f"✅ Final Data: user_id={user_id}, closed_pid={closed_pid}, active_pid={active_pid}, proposed_pid={proposed_pid}, dropped_pid={dropped_pid}")

            insert_survey_response(cursor, user_id, ward_id, evaluation_date, closed_pid, active_pid, proposed_pid, dropped_pid, responses, suggestions)
        
        connection.commit()
        response = {"status": "success", "message": "Survey submitted successfully"}
    except Exception as ex:
        error_details = traceback.format_exc()
        print(f"ERROR TRACE:\n{error_details}")
        response = {"status": "error", "message": f"Unexpected error: {str(ex)}", "trace": error_details}
    finally:
        cursor.close()
        connection.close()

    print("Content-Type: application/json\n")
    print(json.dumps(response))

if __name__ == "__main__":
    main()
