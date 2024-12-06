import requests
import json
import base64

# Configuration

# Headers
manage_engine_headers = {"Authorization": f"Bearer {MANAGE_ENGINE_TOKEN}"}
azure_devops_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {base64.b64encode(f':{AZURE_DEVOPS_TOKEN}'.encode()).decode()}"
}

def migrate_projects_to_projects():
    print("Starting project migration...")

    # Fetch projects from ManageEngine
    response = requests.get(MANAGE_ENGINE_PROJECTS_URL, headers=manage_engine_headers)
    print(f"GET response: {response.status_code} {response.text}")  # Debug output
    
    if response.status_code == 200:
        projects_data = response.json().get("projects", [])
        print(f"Projects data: {projects_data}")  # Debug output

        for project_item in projects_data:
            project_data = {
                "name": project_item.get("project_name", "Unnamed Project"),
                "description": project_item.get("description", "No description available.")
            }
            url = f"https://dev.azure.com/{AZURE_DEVOPS_ORGANIZATION}/_apis/projects?api-version=6.0"
            
            # Create project in Azure DevOps
            response = requests.post(url, headers=azure_devops_headers, data=json.dumps(project_data))
            print(f"POST response: {response.status_code} {response.text}")  # Debug output
            if response.status_code == 200:
                print(f"Successfully created project: {project_data['name']}")
            else:
                print(f"Failed to create project: {response.status_code} {response.text}")
    else:
        print("Failed to fetch projects from ManageEngine.")

# Run migration function
if __name__ == "__main__":
    try:
        migrate_projects_to_projects()
        print("Migration script executed successfully.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")
