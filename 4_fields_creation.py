import requests
import json

# Jira Cloud API credentials
JIRA_URL = "CCCCCCC"
EMAIL = "CCCCCCC"
API_TOKEN = "XXXXXXX"

# Headers for authentication
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"Basic {requests.auth._basic_auth_str(EMAIL, API_TOKEN)}"
}

# Custom field details
custom_fields = [
    {"name": "Country", "type": "com.atlassian.jira.plugin.system.customfieldtypes:select", "options": ["USA", "Canada", "India", "Germany", "Australia"]},
    {"name": "State", "type": "com.atlassian.jira.plugin.system.customfieldtypes:select", "options": ["California", "Texas", "Ontario", "Maharashtra", "Bavaria", "New South Wales"]},
    {"name": "District", "type": "com.atlassian.jira.plugin.system.customfieldtypes:select", "options": ["Los Angeles", "Houston", "Toronto", "Pune", "Munich", "Sydney"]},
    {"name": "Village/Town", "type": "com.atlassian.jira.plugin.system.customfieldtypes:select", "options": ["Santa Monica", "Sugar Land", "Brampton", "Shivaji Nagar", "Schwabing", "Bondi Beach"]}
]

# Function to create custom fields
def create_custom_field(name, type):
    url = f"{JIRA_URL}/rest/api/3/field"
    payload = {
        "name": name,
        "description": f"Custom field for {name}",
        "type": type
    }
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 201:
        field_id = response.json()["id"]
        print(f"Created field: {name} (ID: {field_id})")
        return field_id
    else:
        print(f"Failed to create field {name}: {response.text}")
        return None

# Function to add options to a custom field
def add_options_to_field(field_id, options):
    url = f"{JIRA_URL}/rest/api/3/customField/{field_id}/option"
    for option in options:
        payload = {"value": option}
        response = requests.post(url, headers=HEADERS, json=payload)
        if response.status_code == 201:
            print(f"Added option: {option} to field ID: {field_id}")
        else:
            print(f"Failed to add option {option}: {response.text}")

# Create fields and add options
for field in custom_fields:
    field_id = create_custom_field(field["name"], field["type"])
    if field_id:
        add_options_to_field(field_id, field["options"])
