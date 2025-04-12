import requests
import csv
from requests.auth import HTTPBasicAuth

# Jira API Credentials
JIRA_URL = "XXXXX"
USERNAME = "XXXXXX"
API_TOKEN = "XXXXXX"

# API Endpoints
PROJECTS_ENDPOINT = f"{JIRA_URL}/rest/api/3/project/search?expand=lead"
USER_DETAILS_ENDPOINT = f"{JIRA_URL}/rest/api/3/user"

# Function to get user details (including email)
def get_user_email(account_id):
    user_response = requests.get(
        f"{USER_DETAILS_ENDPOINT}?accountId={account_id}",
        auth=HTTPBasicAuth(USERNAME, API_TOKEN),
        headers={"Accept": "application/json"},
    )
    if user_response.status_code == 200:
        return user_response.json().get("emailAddress", "Email Hidden")
    return "Not Found"

# Get project details
response = requests.get(
    PROJECTS_ENDPOINT,
    auth=HTTPBasicAuth(USERNAME, API_TOKEN),
    headers={"Accept": "application/json"},
)

if response.status_code == 200:
    projects_data = response.json()
    projects = projects_data.get("values", [])

    csv_filename = "jira_projects_with_leads.csv"

    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Project Name", "Project Key", "Project Lead", "Lead Email"])

        for project in projects:
            project_name = project.get("name", "N/A")
            project_key = project.get("key", "N/A")
            lead = project.get("lead", {})

            lead_name = lead.get("displayName", "No Lead Assigned")
            account_id = lead.get("accountId", None)

            lead_email = get_user_email(account_id) if account_id else "No Email Available"
            writer.writerow([project_name, project_key, lead_name, lead_email])

    print(f"✅ CSV file '{csv_filename}' has been created successfully.")
else:
    print(f"❌ Error: {response.status_code}, {response.text}")