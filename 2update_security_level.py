import requests
import time

# Jira API credentials
JIRA_URL = "XXXXXX"
JIRA_USER = "XXXXX"
JIRA_API_TOKEN = "XXXXXX"

# JQL query to fetch issues
JQL_QUERY = "Key = HELP-33782"

# Use a session for better authentication handling
session = requests.Session()
session.auth = (JIRA_USER, JIRA_API_TOKEN)
session.headers.update({"Content-Type": "application/json"})

def get_issue_keys():
    """Fetch issue keys in batches of 100 using JQL"""
    issue_keys = []
    start_at = 0
    max_results = 100

    while True:
        url = f"{JIRA_URL}/rest/api/3/search"
        params = {
            "jql": JQL_QUERY,
            "startAt": start_at,
            "maxResults": max_results,
            "fields": "key"
        }
        response = session.get(url, params=params)

        if response.status_code != 200:
            print(f"❌ Failed to fetch issues: {response.text}")
            return []

        data = response.json()
        issues = data.get("issues", [])
        issue_keys.extend([issue["key"] for issue in issues])

        print(f"✅ Fetched {len(issues)} issues (Total: {len(issue_keys)})")

        if len(issues) < max_results:
            break  # No more issues left to fetch

        start_at += max_results
        time.sleep(1)  # Avoid hitting rate limits

    return issue_keys

def update_security_level(issue_key):
    """Update security level for a single issue"""
    url = f"{JIRA_URL}/rest/api/3/issue/{issue_key}"
    payload = {
        "fields": {
            "security": {"name": "Sensitive Cases"}
        }
    }

    response = session.put(url, json=payload)

    if response.status_code == 204:
        print(f"✅ Updated security level for issue {issue_key}")
    else:
        print(f"❌ Failed to update issue {issue_key}: {response.text}")

def bulk_update_security_level(issue_keys):
    """Update security level for each issue one by one"""
    for issue in issue_keys:
        update_security_level(issue)
        time.sleep(1)  # Avoid hitting rate limits

# Run the script
if __name__ == "__main__":
    issues = get_issue_keys()
    if issues:
        print(f"🔄 Total issues to update: {len(issues)}")
        bulk_update_security_level(issues)
    else:
        print("⚠️ No issues found matching JQL.")