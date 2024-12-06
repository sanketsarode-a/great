import requests
import json
import base64

# Configuration

# Headers
manage_engine_headers = {"Authorization": f"Bearer {MANAGE_ENGINE_TOKEN}"}
azure_devops_headers = {
    "Content-Type": "application/json-patch+json",
    "Authorization": f"Basic {base64.b64encode(f':{AZURE_DEVOPS_TOKEN}'.encode()).decode()}"
}

def migrate_problems_to_issues():
    # Get the problems from ManageEngine
    response = requests.get(MANAGE_ENGINE_PROBLEMS_URL, headers=manage_engine_headers)

    # Check for successful response
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        return

    # Try parsing the response as JSON
    try:
        problems_data = response.json().get("problems", [])
    except json.decoder.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Response: {response.text}")
        return

    if not problems_data:
        print("No problems found in the response.")
        return

    for problem_item in problems_data:
        # Debugging: Print problem_item to ensure the title is present
        print(f"Problem Item: {problem_item}")
        
        # Correctly map title and description
        title = problem_item.get("title", "Untitled Problem")  # Use 'title' instead of 'subject'
        description = problem_item.get("description", "No description available.")

        # Print to debug the extracted title and description
        print(f"Title: {title}")
        print(f"Description: {description}")
        
        # Prepare issue data with fields for Azure DevOps
        issue_data = [
            {"op": "add", "path": "/fields/System.Title", "value": title},
            {"op": "add", "path": "/fields/System.Description", "value": description},
            {"op": "add", "path": "/fields/Microsoft.VSTS.Common.Priority", "value": 1},
            {"op": "add", "path": "/fields/System.State", "value": "To Do"}  # Ensure To Do is valid state in Azure DevOps
        ]
        
        # Azure DevOps Work Item URL for Issues
        url = f"https://dev.azure.com/{AZURE_DEVOPS_ORGANIZATION}/{AZURE_DEVOPS_PROJECT}/_apis/wit/workitems/$Issue?api-version=6.0"
        
        # Send the request to create the work item (Issue) in Azure DevOps
        response = requests.post(url, headers=azure_devops_headers, data=json.dumps(issue_data))

        # Handle the response from Azure DevOps
        if response.status_code == 200:
            print(f"Successfully created issue for problem: {title}")
            print(f"Issue ID: {response.json().get('id')}")
        else:
            print(f"Error creating issue for problem: {title}")
            print(f"Azure DevOps Response Code: {response.status_code}")
            print(f"Response: {response.text}")

# Run the migration
migrate_problems_to_issues()
