import requests
import json
import base64
import time


# Headers
manage_engine_headers = {"Authorization": f"Bearer {MANAGE_ENGINE_TOKEN}"}
azure_devops_headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {base64.b64encode(f':{AZURE_DEVOPS_TOKEN}'.encode()).decode()}"
}

def migrate_changes_to_releases():
    # Get the changes from ManageEngine
    response = requests.get(MANAGE_ENGINE_CHANGES_URL, headers=manage_engine_headers)
    changes_data = response.json().get("changes", [])

    for change_item in changes_data:
        title = change_item.get("title", "Untitled Change")
        description = change_item.get("description", "No description available.")
        
        # Create Release Data
        release_data = {
            "definitionReference": {"id": 1},  # Replace with your actual Release Definition ID
            "description": description,
            "reason": "Manual",
            "isDraft": False,
            "artifacts": [
                {
                    "alias": "YourArtifactAlias",  # Replace with your artifact alias
                    "instanceReference": {
                        "id": "YourArtifactID",  # Replace with the actual artifact ID (e.g., build ID)
                    }
                }
            ]
        }

        # Trigger the Release Pipeline
        release_url = f"https://vsrm.dev.azure.com/{AZURE_DEVOPS_ORGANIZATION}/{AZURE_DEVOPS_PROJECT}/_apis/release/releases?api-version=7.1"
        release_response = requests.post(release_url, headers=azure_devops_headers, data=json.dumps(release_data))

        # Check if the request was successful
        if release_response.status_code == 200:
            try:
                release_result = release_response.json()
                print(f"Release created: {release_result.get('id')} for change: {title}")
            except json.decoder.JSONDecodeError:
                print(f"Error parsing JSON response: {release_response.text}")
        else:
            print(f"Error creating release. Status Code: {release_response.status_code}")
            print(f"Response: {release_response.text}")
        
        # Wait to avoid rate limiting issues
        time.sleep(1)

# Run the migration
migrate_changes_to_releases()
