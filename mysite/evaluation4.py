import json
import pymysql
from dbcon import get_database_connection

def calculate_avg_scores():
    conn = get_database_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Fetch all records from the stats table
    query = """
        SELECT county_id, project_completion, completion_percentage, initiative, proposal_success, 
               project_awareness, effective_communication, impact_on_the_community, public_participation, 
               project_management, budget_allocation_awareness, financial_management, 
               infrastructure_development, sustainability, inclusivity, impact_on_specific_demographics, 
               total_score
        FROM stats
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    stats2 = {}
    counts = {}

    for row in rows:
        county_id = row['county_id']
        scores = [
            row['project_completion'], row['completion_percentage'], row['initiative'],
            row['proposal_success'], row['project_awareness'], row['effective_communication'],
            row['impact_on_the_community'], row['public_participation'], row['project_management'],
            row['budget_allocation_awareness'], row['financial_management'], row['infrastructure_development'],
            row['sustainability'], row['inclusivity'], row['impact_on_specific_demographics'], row['total_score']
        ]

        if county_id not in stats2:
            stats2[county_id] = [0.0] * len(scores)
            counts[county_id] = 0

        stats2[county_id] = [sum(x) for x in zip(stats2[county_id], scores)]
        counts[county_id] += 1

    for county_id in stats2:
        stats2[county_id] = [score / counts[county_id] for score in stats2[county_id]]

    cursor.execute("DELETE FROM stats2")
    conn.commit()

    for county_id, avg_scores in stats2.items():
        cursor.execute("""
            INSERT INTO stats2 (county_id, project_completion, completion_percentage, initiative, 
                                proposal_success, project_awareness, effective_communication, 
                                impact_on_the_community, public_participation, project_management, 
                                budget_allocation_awareness, financial_management, 
                                infrastructure_development, sustainability, inclusivity, 
                                impact_on_specific_demographics, total_score) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, [county_id] + avg_scores)
    
    conn.commit()

    cursor.execute("SELECT * FROM stats2")
    stats2_rows = cursor.fetchall()

    data = []
    for row in stats2_rows:
        data.append({
            'county_id': row['county_id'],
            'project_completion': round(row['project_completion'], 2),
            'completion_percentage': round(row['completion_percentage'], 2),
            'initiative': round(row['initiative'], 2),
            'proposal_success': round(row['proposal_success'], 2),
            'project_awareness': round(row['project_awareness'], 2),
            'effective_communication': round(row['effective_communication'], 2),
            'impact_on_the_community': round(row['impact_on_the_community'], 2),
            'public_participation': round(row['public_participation'], 2),
            'project_management': round(row['project_management'], 2),
            'budget_allocation_awareness': round(row['budget_allocation_awareness'], 2),
            'financial_management': round(row['financial_management'], 2),
            'infrastructure_development': round(row['infrastructure_development'], 2),
            'sustainability': round(row['sustainability'], 2),
            'inclusivity': round(row['inclusivity'], 2),
            'impact_on_specific_demographics': round(row['impact_on_specific_demographics'], 2),
            'total_score': round(row['total_score'], 2)
        })

    cursor.close()
    conn.close()

    return data


# WSGI entrypoint
def application(environ, start_response):
    try:
        if environ['REQUEST_METHOD'] != 'GET':
            status = '405 Method Not Allowed'
            response_body = json.dumps({'error': 'Only GET method allowed'})
        else:
            status = '200 OK'
            response_body = json.dumps(calculate_avg_scores())

    except Exception as e:
        status = '500 Internal Server Error'
        response_body = json.dumps({'error': str(e)})

    headers = [('Content-Type', 'application/json'), ('Content-Length', str(len(response_body)))]
    start_response(status, headers)
    return [response_body.encode('utf-8')]
