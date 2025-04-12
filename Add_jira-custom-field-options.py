import json
import requests
from requests.auth import HTTPBasicAuth
import datetime
import os
import tkinter as tk
from tkinter import messagebox

################ Populate below variables ################

# LOG_TYPE: 1 - print to console, 0 - print to logfile
LOG_TYPE = 1

################ End of populate below variables ################

REST = "rest"
API = "api"
APIVERSION = "3"
CUR_CF_OPTIONS = {}
CUR_CF_OPTIONS_STATUS = {}
HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}
LOGFILENAME = "Output_" + datetime.datetime.now().strftime("%m_%d_%y_%H_%M_%S") + ".log"

if not os.path.exists("logs"):
    os.mkdir("logs")

LOGFILE_PATH = os.path.join("logs", LOGFILENAME)

# Define logging function
def log_IT(msg):
    log_msg = f"{datetime.datetime.now()} {msg}"
    if LOG_TYPE == 1:
        print(log_msg)
    else:
        with open(LOGFILE_PATH, "a") as log_file:
            log_file.write(f"{log_msg}\n")

# Define main application form class
class InputForm(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Jira Custom Field Input")
        
        # Create and place widgets
        tk.Label(self, text="Jira URL (e.g., https://yourcompany.atlassian.net):").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.jira_url_entry = tk.Entry(self, width=50)
        self.jira_url_entry.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self, text="Jira Username/Email:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.jira_username_entry = tk.Entry(self, width=50)
        self.jira_username_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(self, text="Jira API Token:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.jira_api_token_entry = tk.Entry(self, width=50, show='*')
        self.jira_api_token_entry.grid(row=2, column=1, padx=10, pady=5)

        tk.Label(self, text="Custom Field Name:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.custom_field_name_entry = tk.Entry(self, width=50)
        self.custom_field_name_entry.grid(row=3, column=1, padx=10, pady=5)

        tk.Label(self, text="Context ID:").grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.context_id_entry = tk.Entry(self, width=50)
        self.context_id_entry.grid(row=4, column=1, padx=10, pady=5)

        tk.Label(self, text="Custom Field Options (one per line):").grid(row=5, column=0, padx=10, pady=5, sticky="w")
        self.options_text = tk.Text(self, height=10, width=50)
        self.options_text.grid(row=5, column=1, padx=10, pady=5)

        self.submit_button = tk.Button(self, text="Submit", command=self.on_submit)
        self.submit_button.grid(row=6, column=1, padx=10, pady=10, sticky="e")

    def on_submit(self):
        global JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN, custom_field_name, context_id, user_values

        # Retrieve values from form
        JIRA_URL = self.jira_url_entry.get().strip()
        JIRA_USERNAME = self.jira_username_entry.get().strip()
        JIRA_API_TOKEN = self.jira_api_token_entry.get().strip()
        custom_field_name = self.custom_field_name_entry.get().strip()
        context_id = self.context_id_entry.get().strip()
        user_values = [line.strip() for line in self.options_text.get("1.0", tk.END).split('\n') if line.strip()]

        # Validate inputs
        if not all([JIRA_URL, JIRA_USERNAME, JIRA_API_TOKEN, custom_field_name, context_id]):
            messagebox.showerror("Error", "All fields must be filled in.")
            return
        
        if not user_values:
            messagebox.showerror("Error", "At least one custom field option must be provided.")
            return

        self.destroy()
        main_logic()

# Main function
def main_logic():
    log_IT(f"INFO    : Getting all custom fields in Jira")
    customfields_id = get_all_customfields_id()

    log_IT(f"INFO    : Getting the custom field ID of {custom_field_name}")
    cur_cf_id = get_cur_cf_id(customfields_id, custom_field_name)
    log_IT(f"INFO    : Custom field ID of {custom_field_name} is {cur_cf_id[0]}")

    # Get current options in Jira for the custom field
    get_cur_field_options(cur_cf_id[0], context_id)

    # Process user input values
    for value in user_values:
        value_lower = value.lower()
        if value_lower in CUR_CF_OPTIONS:
            if CUR_CF_OPTIONS_STATUS[value_lower]:
                # Option is disabled in Jira, enable it
                update_customfield_options(value, cur_cf_id[0], context_id)
            else:
                # Option is already enabled in Jira, ignore it
                log_IT(f"INFO    : Option '{value}' already exists and is enabled in Jira, skipping.")
        else:
            # Option does not exist in Jira, add it
            add_customfield_options(value, cur_cf_id[0], context_id)

    log_IT("INFO    : Completed, script ran successfully")

def option_to_add_json_format(option):
    return {"options": [{"disabled": False, "value": option}]}

def option_to_update_json_format(option):
    return {"options": [{"disabled": False, "value": option, "id": CUR_CF_OPTIONS[option.lower()]}]}

def add_customfield_options(option_to_add, cur_cf_id, context_id):
    option_to_add_json = json.dumps(option_to_add_json_format(option_to_add))
    jira_rest_end_point = build_jira_endpoint(f"/field/{cur_cf_id}/context/{context_id}/option")
    response = requests.request("POST", jira_rest_end_point, headers=HEADERS, auth=HTTPBasicAuth(JIRA_USERNAME, JIRA_API_TOKEN), data=option_to_add_json)
    if check_response_code(response.status_code):
        log_IT(f"INFO    : Added option - {option_to_add}")
    else:
        log_IT(f"ERROR   : Failed to add option {option_to_add} with error - {response.text} and error code is {response.status_code}")
        exit()

def update_customfield_options(option_to_add, cur_cf_id, context_id):
    option_to_update_json = json.dumps(option_to_update_json_format(option_to_add))
    jira_rest_end_point = build_jira_endpoint(f"/field/{cur_cf_id}/context/{context_id}/option")
    response = requests.request("PUT", jira_rest_end_point, headers=HEADERS, auth=HTTPBasicAuth(JIRA_USERNAME, JIRA_API_TOKEN), data=option_to_update_json)
    if check_response_code(response.status_code):
        log_IT(f"INFO    : Enabled option - {option_to_add}")
    else:
        log_IT(f"ERROR   : Failed to enable option {option_to_add} with error - {response.text} and error code is {response.status_code}")
        exit()

def get_all_customfields_id():
    customfields_id = {}
    start_at = 0
    is_last = False
    
    while not is_last:
        jira_rest_end_point = build_jira_endpoint(f"/field/search?startAt={start_at}&maxResults=50")
        response = requests.request("GET", jira_rest_end_point, headers=HEADERS, auth=HTTPBasicAuth(JIRA_USERNAME, JIRA_API_TOKEN))
        if check_response_code(response.status_code):
            response_json = json.loads(response.text)
            for customfield in response_json["values"]:
                if customfield["name"].lower() not in customfields_id:
                    customfields_id[customfield["name"].lower()] = [customfield["id"]]
                else:
                    customfields_id[customfield["name"].lower()].append(customfield["id"])
        else:
            log_IT(f"ERROR   : Failed to get all custom fields from Jira with error - {response.text} and error code is {response.status_code}")
            exit()
        start_at += 50
        is_last = response_json["isLast"]
    
    return customfields_id

def get_cur_cf_id(customfields_id, custom_field_name):
    if custom_field_name.lower() not in customfields_id or len(customfields_id[custom_field_name.lower()]) > 1:
        log_IT(f"ERROR   : Either custom field name '{custom_field_name}' is empty or multiple field IDs found.")
        exit()
    return customfields_id[custom_field_name.lower()]

def get_cur_field_options(cur_cf_id, context_id):
    start_at = 0
    is_last = False
    while not is_last:
        jira_rest_end_point = build_jira_endpoint(f"/field/{cur_cf_id}/context/{context_id}/option?startAt={start_at}&maxResults=50")
        response = requests.request("GET", jira_rest_end_point, headers=HEADERS, auth=HTTPBasicAuth(JIRA_USERNAME, JIRA_API_TOKEN))
        if check_response_code(response.status_code):
            response_json = json.loads(response.text)
            for options in response_json["values"]:
                CUR_CF_OPTIONS[options["value"].lower()] = options["id"]
                CUR_CF_OPTIONS_STATUS[options["value"].lower()] = options["disabled"]
        else:
            log_IT(f"ERROR   : Failed to get current options of custom field with error - {response.text} and error code is {response.status_code}")
            exit()
        start_at += 50
        is_last = response_json["isLast"]

def build_jira_endpoint(endpoint):
    return f"{JIRA_URL}/{REST}/{API}/{APIVERSION}{endpoint}"

def check_response_code(status_code):
    return status_code == 200

if __name__ == "__main__":
    app = InputForm()
    app.mainloop()