#!/usr/bin/env python3  # Use this for CGI scripts
import cgi
import cgitb
import json
import pymysql  # Add this import
from dbcon import get_database_connection

cgitb.enable()

# Calculate various project-related metrics
def calculate_project_completion(ward_data):
    """Calculate the percentage of completed projects."""
    total_closed = sum(1 for row in ward_data if isinstance(row, dict) and row.get('closed_pid'))
    total_projects = len(ward_data)  # Total projects should be the length of the dataset
    
    return (total_closed / total_projects) * 100 if total_projects > 0 else 0.0


def calculate_completion_percentage(ward_data):
    """Calculate the percentage of completed projects compared to active projects."""
    total_closed = sum(1 for row in ward_data if isinstance(row, dict) and row.get('closed_pid'))
    total_active = sum(1 for row in ward_data if isinstance(row, dict) and row.get('active_pid'))
    total_projects = total_closed + total_active  # Only consider closed and active projects
    
    return (total_closed / total_projects) * 100 if total_projects > 0 else 0.0


def calculate_initiative(ward_data):
    """Measure the percentage of proposed projects."""
    total_proposed = sum(1 for row in ward_data if isinstance(row, dict) and row.get('proposed_pid'))
    total_projects = len(ward_data)  # Consider all projects
    
    return (total_proposed / total_projects) * 100 if total_projects > 0 else 0.0


def calculate_proposal_success(ward_data):
    """Measure the success rate of proposed projects (i.e., not dropped)."""
    total_proposed = sum(1 for row in ward_data if isinstance(row, dict) and row.get('proposed_pid'))
    total_dropped = sum(1 for row in ward_data if isinstance(row, dict) and row.get('dropped_pid'))
    
    return ((total_proposed - total_dropped) / total_proposed) * 100 if total_proposed > 0 else 0.0




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

# Main function to calculate and insert statistics
def calculate_stats():
    conn = get_database_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Fetch all records from evaluation table
    query = """
        SELECT id, ward_id, closed_pid, active_pid, ward_id, proposed_pid, dropped_pid, 
               project_awareness, projects_communication_channels, project_impact,
               project_participation, public_input, project_completion_status, project_planning,
               budget_allocation_awareness, financial_management, infrastructure_development,
               environmental_impact, project_negative_effects, inclusivity_in_project_implementation,
               impact_on_specific_demographics 
        FROM evaluation
    """
    cursor.execute(query)
    rows = cursor.fetchall()

    # Dictionaries to store aggregated scores and counts by ward_id
    stats = {}
    counts = {}

    # Calculate scores for each record and aggregate by ward_id
    for row in rows:
        ward_id = row['ward_id']
        project_completion_score = calculate_project_completion(row)
        completion_percentage_score = calculate_completion_percentage(row)
        initiative_score = calculate_initiative(row)
        proposal_success_score = calculate_proposal_success(row)
        project_awareness_score = calculate_project_awareness(row)
        effective_communication_score = calculate_effective_communication(row)
        impact_on_the_community_score = calculate_impact_on_the_community(row)
        public_participation_score = calculate_public_participation(row)
        project_management_score = calculate_project_management(row)
        budget_allocation_awareness_score = calculate_budget_allocation_awareness(row)
        financial_management_score = calculate_financial_management(row)
        infrastructure_development_score = calculate_infrastructure_development(row)
        sustainability_score = calculate_sustainability(row)
        inclusivity_score = calculate_inclusivity(row)
        impact_on_specific_demographics_score = calculate_impact_on_specific_demographics(row)

        total_score = (
            project_completion_score + completion_percentage_score + initiative_score +
            proposal_success_score + project_awareness_score + effective_communication_score +
            impact_on_the_community_score + public_participation_score + project_management_score +
            budget_allocation_awareness_score + financial_management_score + infrastructure_development_score +
            sustainability_score + inclusivity_score + impact_on_specific_demographics_score
        )

        if ward_id not in stats:
            stats[ward_id] = {
                'project_completion': project_completion_score,
                'completion_percentage': completion_percentage_score,
                'initiative': initiative_score,
                'proposal_success': proposal_success_score,
                'project_awareness': project_awareness_score,
                'effective_communication': effective_communication_score,
                'impact_on_the_community': impact_on_the_community_score,
                'public_participation': public_participation_score,
                'project_management': project_management_score,
                'budget_allocation_awareness': budget_allocation_awareness_score,
                'financial_management': financial_management_score,
                'infrastructure_development': infrastructure_development_score,
                'sustainability': sustainability_score,
                'inclusivity': inclusivity_score,
                'impact_on_specific_demographics': impact_on_specific_demographics_score,
                'total_score': total_score
            }
            counts[ward_id] = 1
        else:
            stats[ward_id]['project_completion'] += project_completion_score
            stats[ward_id]['completion_percentage'] += completion_percentage_score
            stats[ward_id]['initiative'] += initiative_score
            stats[ward_id]['proposal_success'] += proposal_success_score
            stats[ward_id]['project_awareness'] += project_awareness_score
            stats[ward_id]['effective_communication'] += effective_communication_score
            stats[ward_id]['impact_on_the_community'] += impact_on_the_community_score
            stats[ward_id]['public_participation'] += public_participation_score
            stats[ward_id]['project_management'] += project_management_score
            stats[ward_id]['budget_allocation_awareness'] += budget_allocation_awareness_score
            stats[ward_id]['financial_management'] += financial_management_score
            stats[ward_id]['infrastructure_development'] += infrastructure_development_score
            stats[ward_id]['sustainability'] += sustainability_score
            stats[ward_id]['inclusivity'] += inclusivity_score
            stats[ward_id]['impact_on_specific_demographics'] += impact_on_specific_demographics_score
            stats[ward_id]['total_score'] += total_score
            counts[ward_id] += 1

    # Insert or update aggregated statistics for each ward
    insert_query = """
    INSERT INTO stats (ward_id, project_completion, completion_percentage, initiative, proposal_success,
                       project_awareness, effective_communication, impact_on_the_community,
                       public_participation, project_management, budget_allocation_awareness,
                       financial_management, infrastructure_development, sustainability, inclusivity,
                       impact_on_specific_demographics, total_score)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
        project_completion=VALUES(project_completion),
        completion_percentage=VALUES(completion_percentage),
        initiative=VALUES(initiative),
        proposal_success=VALUES(proposal_success),
        project_awareness=VALUES(project_awareness),
        effective_communication=VALUES(effective_communication),
        impact_on_the_community=VALUES(impact_on_the_community),
        public_participation=VALUES(public_participation),
        project_management=VALUES(project_management),
        budget_allocation_awareness=VALUES(budget_allocation_awareness),
        financial_management=VALUES(financial_management),
        infrastructure_development=VALUES(infrastructure_development),
        sustainability=VALUES(sustainability),
        inclusivity=VALUES(inclusivity),
        impact_on_specific_demographics=VALUES(impact_on_specific_demographics),
        total_score=VALUES(total_score)
    """
    
    for ward_id, scores in stats.items():
        cursor.execute(insert_query, (
            ward_id,
            scores['project_completion'] / counts[ward_id],
            scores['completion_percentage'] / counts[ward_id],
            scores['initiative'] / counts[ward_id],
            scores['proposal_success'] / counts[ward_id],
            scores['project_awareness'] / counts[ward_id],
            scores['effective_communication'] / counts[ward_id],
            scores['impact_on_the_community'] / counts[ward_id],
            scores['public_participation'] / counts[ward_id],
            scores['project_management'] / counts[ward_id],
            scores['budget_allocation_awareness'] / counts[ward_id],
            scores['financial_management'] / counts[ward_id],
            scores['infrastructure_development'] / counts[ward_id],
            scores['sustainability'] / counts[ward_id],
            scores['inclusivity'] / counts[ward_id],
            scores['impact_on_specific_demographics'] / counts[ward_id],
            scores['total_score'] / counts[ward_id]
        ))

    conn.commit()
    conn.close()

    # Return success message in JSON
    print("Content-type: application/json\n")
    print(json.dumps({"message": "Stats calculated and inserted successfully."}))

if __name__ == "__main__":
    calculate_stats()