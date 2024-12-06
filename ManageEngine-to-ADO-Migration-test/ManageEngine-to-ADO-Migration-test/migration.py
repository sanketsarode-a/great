import requests
import json
import base64

# Configuration

# Headers for authentication
manage_engine_headers = {
    "Authorization": f"Bearer {MANAGE_ENGINE_TOKEN}"
}

username = ""  # Provide your Azure DevOps username if needed
azure_devops_headers = {
    "Content-Type": "application/json-patch+json",
    "Authorization": f"Basic {base64.b64encode(f'{username}:{AZURE_DEVOPS_TOKEN}'.encode()).decode()}"
}

def fetch_manage_engine_data():
    response = requests.get(MANAGE_ENGINE_API_URL, headers=manage_engine_headers)
    
    if response.status_code == 200:
        print("Data fetched successfully from ManageEngine.")
        return response.json()  
    else:
        print(f"Failed to fetch data from ManageEngine. Status code: {response.status_code}, Response: {response.text}")
        return None  

def transform_data(data):
    print("Inspecting fetched data:")
    print(data)

    requests_data = data.get("requests", [])
    
    if not requests_data:
        print("No requests data found. Exiting transformation.")
        return []

    transformed_data = []
    for item in requests_data:
        if isinstance(item, dict):
            status_name = item.get("status", {}).get("name")
            priority_value = 2 if status_name == "Open" else 3  
            requester_email = item.get("requester", {}).get("email_id")
            assigned_to_email = requester_email if requester_email else "himanshut0766@gmail.com"

            transformed_item = {
                "title": item.get("subject") or "Untitled",
                "description": item.get("subject") or "No description provided.",
                "priority": priority_value,
                "assignedTo": assigned_to_email,
                "state": "To Do"  # Set the state to "To Do"
            }
            transformed_data.append(transformed_item)
        else:
            print(f"Skipping non-dictionary item: {item}")
    return transformed_data

def create_azure_devops_work_item(work_item):
    work_item_type = "Task"
    url = f"https://dev.azure.com/{AZURE_DEVOPS_ORGANIZATION}/{AZURE_DEVOPS_PROJECT}/_apis/wit/workitems/${work_item_type}?api-version=6.0"
    
    data = [
        {"op": "add", "path": "/fields/System.Title", "value": work_item.get("title")},
        {"op": "add", "path": "/fields/System.Description", "value": work_item.get("description")},
        {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority", "value": work_item.get("priority")},
        {"op": "add", "path": "/fields/System.State", "value": work_item.get("state")}
    ]

    print(f"Creating work item with the following data: {json.dumps(data, indent=2)}")

    response = requests.post(url, headers=azure_devops_headers, data=json.dumps(data))
    if response.status_code in [200, 201]:
        print(f"Work item '{work_item['title']}' created successfully.")
    else:
        print(f"Failed to create work item '{work_item['title']}'. Status code: {response.status_code}, Response: {response.text}")

def migrate_data():
    manage_engine_data = fetch_manage_engine_data()
    
    if not manage_engine_data:
        print("No data fetched from ManageEngine. Exiting migration.")
        return

    transformed_data = transform_data(manage_engine_data)

    for work_item in transformed_data:
        create_azure_devops_work_item(work_item)

if __name__ == "__main__":
    migrate_data()
