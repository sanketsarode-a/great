import requests
import json
import base64
import time

# Configuration

# Headers
manage_engine_headers = {"Authorization": f"Bearer {MANAGE_ENGINE_TOKEN}"}
azure_devops_headers = {
    "Content-Type": "application/json-patch+json",
    "Authorization": f"Basic {base64.b64encode(f':{AZURE_DEVOPS_TOKEN}'.encode()).decode()}"
}

def migrate_changes_to_tasks():
    # Get changes from ManageEngine
    try:
        response = requests.get(MANAGE_ENGINE_CHANGES_URL, headers=manage_engine_headers)
        response.raise_for_status()
        changes_data = response.json().get("changes", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching changes from ManageEngine: {e}")
        return
    
    # Iterate over each change item and create a task in Azure DevOps
    for change_item in changes_data:
        title = change_item.get("title", "Untitled Change")
        description = change_item.get("description", "No description available.")

        task_data = [
            {"op": "add", "path": "/fields/System.Title", "value": title},
            {"op": "add", "path": "/fields/System.Description", "value": description},
            {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority", "value": 2},
            {"op": "add", "path": "/fields/System.State", "value": "To Do"}  # Adjust if needed based on allowed states
        ]

        # Azure DevOps API URL for creating a work item
        url = f"https://dev.azure.com/{AZURE_DEVOPS_ORGANIZATION}/{AZURE_DEVOPS_PROJECT}/_apis/wit/workitems/$Task?api-version=6.0"

        try:
            # Create task in Azure DevOps
            task_response = requests.post(url, headers=azure_devops_headers, data=json.dumps(task_data))
            task_response.raise_for_status()
            task_result = task_response.json()
            print(f"Successfully created task with ID: {task_result.get('id')} for change: {title}")
        except requests.exceptions.RequestException as e:
            print(f"Error creating task for change '{title}': {e}")
        except json.JSONDecodeError:
            print("Error decoding response JSON for task creation")

        # Wait to avoid rate limiting issues
        time.sleep(1)

migrate_changes_to_tasks()
