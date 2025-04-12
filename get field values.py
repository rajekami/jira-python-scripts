import requests
import csv

def fetch_jira_field_details(jira_url, username, api_token, project_keys):
    # Construct the API endpoint URL
    api_endpoint = f"{jira_url.rstrip('/')}/rest/api/2/issue/createmeta"
    
    # Construct the headers with basic authentication
    headers = {
        "Accept": "application/json"
    }
    
    # Parameters for the API request
    params = {
        "projectKeys": ",".join(project_keys),
        "expand": "projects.issuetypes.fields"
    }
    
    # Make the API request
    try:
        response = requests.get(api_endpoint, headers=headers, auth=(username, api_token), params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from JIRA: {e}")
        return None

def write_to_csv(data, output_file):
    try:
        with open(output_file, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # Write header row
            writer.writerow(["Project Name", "Issue Type", "Screen Name", "Tab Name", "Field Name", "Field ID"])
            
            # Write data rows
            for project in data['projects']:
                for issue_type in project['issuetypes']:
                    for screen_name, screen_fields in issue_type['fields'].items():
                        if 'tab' in screen_fields:
                            for tab_name, tab_fields in screen_fields['tab'].items():
                                if 'fields' in tab_fields:
                                    for field_id, field_details in tab_fields['fields'].items():
                                        writer.writerow([
                                            project['name'],
                                            issue_type['name'],
                                            screen_name,
                                            tab_name,
                                            field_details['name'],
                                            field_id
                                        ])
                                else:
                                    print(f"No fields found in tab '{tab_name}' of screen '{screen_name}'")
                        else:
                            print(f"No 'tab' found in screen '{screen_name}'")
            
        print(f"CSV file '{output_file}' has been successfully created.")
    except IOError as e:
        print(f"Error writing to CSV file: {e}")

if __name__ == "__main__":
    # User inputs
    jira_url = input("Enter JIRA URL (e.g., https://your-jira-instance.atlassian.net): ").strip()
    username = input("Enter JIRA Username: ").strip()
    api_token = input("Enter JIRA API Token (generate one from JIRA profile settings): ").strip()
    project_keys = input("Enter JIRA Project Keys (comma-separated, e.g., SCURM): ").strip().split(',')
    output_file = input("Enter output CSV file name (e.g., jira_fields.csv): ").strip()
    
    # Fetch field details from JIRA
    field_details = fetch_jira_field_details(jira_url, username, api_token, project_keys)
    
    if field_details:
        # Write field details to CSV
        write_to_csv(field_details, output_file)