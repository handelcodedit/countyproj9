import json
import pymysql
from dbcon import get_database_connection

# Scoring functions remain unchanged
def calculate_project_completion(row):
    return 99.0 if row['closed_pid'] else 1.0

def calculate_completion_percentage(row):
    closed_pid_score = 99.0 if row['closed_pid'] else 1.0
    active_pid_score = 1.0 if row['active_pid'] else 99.0
    return (closed_pid_score / (closed_pid_score + active_pid_score)) * 100

def calculate_initiative(row):
    return 99.0 if row['proposed_pid'] else 1.0

def calculate_proposal_success(row):
    proposed_pid_score = 99.0 if row['proposed_pid'] else 1.0
    dropped_pid_score = 1.0 if row['dropped_pid'] else 99.0
    return (proposed_pid_score / (proposed_pid_score + dropped_pid_score)) * 100

def calculate_project_awareness(row):
    if row['project_awareness'] == 'very informed':
        return 100.0
    elif row['project_awareness'] == 'somewhat informed':
        return 50.0
    else:
        return 1.0

def calculate_effective_communication(row):
    return 100.0 if row['projects_communication_channels'] == 'yes' else 1.0

def calculate_impact_on_the_community(row):
    if row['project_impact'] == 'Significant impact':
        return 90.0
    elif row['project_impact'] == 'Moderate impact':
        return 40.0
    else:
        return 1.0

def calculate_public_participation(row):
    project_participation_score = 93.0 if row['project_participation'] == 'yes' else 19.0
    if row['public_input'] == 'A lot':
        public_input_score = 89.0
    elif row['public_input'] == 'Some':
        public_input_score = 33.0
    else:
        public_input_score = 9.0
    return (project_participation_score + public_input_score) / 2

def calculate_project_management(row):
    if row['project_completion_status'] == 'Always':
        project_completion_status_score = 79.0
    elif row['project_completion_status'] == 'Sometimes':
        project_completion_status_score = 29.0
    else:
        project_completion_status_score = 7.0

    if row['project_planning'] == 'Very Effective':
        project_planning_score = 71.0
    elif row['project_planning'] == 'Moderately Effective':
        project_planning_score = 53.0
    else:
        project_planning_score = 16.0
    return (project_completion_status_score + project_planning_score) / 2

def calculate_budget_allocation_awareness(row):
    return 69.0 if row['budget_allocation_awareness'] == 'Yes' else 21.0

def calculate_financial_management(row):
    if row['financial_management'] == 'Excellent':
        return 98.0
    elif row['financial_management'] == 'Good':
        return 79.0
    else:
        return 15.0

def calculate_infrastructure_development(row):
    if row['infrastructure_development'] == 'Satisfactory':
        return 80.0
    elif row['infrastructure_development'] == 'Needs Improvement':
        return 45.0
    else:
        return 5.0

def calculate_sustainability(row):
    if row['environmental_impact'] == 'positive':
        environmental_impact_score = 77.0
    elif row['environmental_impact'] == 'negative':
        environmental_impact_score = 3.0
    else:
        environmental_impact_score = 15.0

    project_negative_effects_score = 13.0 if row['project_negative_effects'] == 'yes' else 83.0
    return (environmental_impact_score + project_negative_effects_score) / 2

def calculate_inclusivity(row):
    return 65.0 if row['inclusivity_in_project_implementation'] == 'Yes' else 10.0

def calculate_impact_on_specific_demographics(row):
    return 75.0 if row['impact_on_specific_demographics'] == 'Yes' else 5.0

def calculate_stats():
    conn = get_database_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    cursor.execute("DELETE FROM stats")
    conn.commit()

    cursor.execute("""
        SELECT id, ward_id, closed_pid, active_pid, proposed_pid, dropped_pid, 
               project_awareness, projects_communication_channels, project_impact,
               project_participation, public_input, project_completion_status, project_planning,
               budget_allocation_awareness, financial_management, infrastructure_development,
               environmental_impact, project_negative_effects, inclusivity_in_project_implementation,
               impact_on_specific_demographics 
        FROM evaluation
    """)
    rows = cursor.fetchall()

    stats = {}
    counts = {}

    for row in rows:
        ward_id = row['ward_id']
        cursor.execute("SELECT county_id FROM project_list WHERE ward_id = %s LIMIT 1", (ward_id,))
        county_result = cursor.fetchone()
        if not county_result:
            continue
        county_id = county_result['county_id']

        scores = {
            'project_completion': calculate_project_completion(row),
            'completion_percentage': calculate_completion_percentage(row),
            'initiative': calculate_initiative(row),
            'proposal_success': calculate_proposal_success(row),
            'project_awareness': calculate_project_awareness(row),
            'effective_communication': calculate_effective_communication(row),
            'impact_on_the_community': calculate_impact_on_the_community(row),
            'public_participation': calculate_public_participation(row),
            'project_management': calculate_project_management(row),
            'budget_allocation_awareness': calculate_budget_allocation_awareness(row),
            'financial_management': calculate_financial_management(row),
            'infrastructure_development': calculate_infrastructure_development(row),
            'sustainability': calculate_sustainability(row),
            'inclusivity': calculate_inclusivity(row),
            'impact_on_specific_demographics': calculate_impact_on_specific_demographics(row),
        }

        scores['total_score'] = sum(scores.values())

        if ward_id not in stats:
            stats[ward_id] = {**scores, 'county_id': county_id}
            counts[ward_id] = 1
        else:
            for key in scores:
                stats[ward_id][key] += scores[key]
            counts[ward_id] += 1

    insert_query = """
    INSERT INTO stats (ward_id, county_id, project_completion, completion_percentage, initiative, proposal_success,
                       project_awareness, effective_communication, impact_on_the_community,
                       public_participation, project_management, budget_allocation_awareness,
                       financial_management, infrastructure_development, sustainability, inclusivity,
                       impact_on_specific_demographics, total_score)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for ward_id, values in stats.items():
        count = counts[ward_id]
        cursor.execute(insert_query, (
            ward_id, values['county_id'],
            *(values[key] / count for key in [
                'project_completion', 'completion_percentage', 'initiative', 'proposal_success',
                'project_awareness', 'effective_communication', 'impact_on_the_community',
                'public_participation', 'project_management', 'budget_allocation_awareness',
                'financial_management', 'infrastructure_development', 'sustainability',
                'inclusivity', 'impact_on_specific_demographics', 'total_score'
            ])
        ))

    conn.commit()

    cursor.execute("SELECT * FROM stats")
    result = cursor.fetchall()
    conn.close()
    return json.dumps(result)

# WSGI application entry point
def application(environ, start_response):
    response_body = calculate_stats()
    status = '200 OK'
    headers = [('Content-Type', 'application/json')]
    start_response(status, headers)
    return [response_body.encode('utf-8')]
