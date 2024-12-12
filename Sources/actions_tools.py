import io
import zipfile

import os
import time 

import requests
import threading

import json
from base64 import b64encode


#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
## https://github.com/settings/tokens
#REPO_NAME = os.getenv('REPO_NAME')
#REPO_OWNER = os.getenv('REPO_OWNER')
#GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')


## https://github.com/test-earth-engine/gee1/tree/main


#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
GITHUB_API_URL = 'https://api.github.com'

headers = {}
headers['Accept'] = 'application/vnd.github.v3+json'
headers['Authorization'] = f'token {GITHUB_TOKEN}'


#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#
def check_github_connection():
    url = f'{GITHUB_API_URL}/repos/{REPO_OWNER}/{REPO_NAME}'
    response = requests.get(url, headers=headers)

    
    status = None 
    if response.status_code == 200:
        status = True
    else:
        status = False

    if status: print(f"'{url}' runnig...")
    return status        


#-----------------------------------------------------------------------------#
def commit_json_to_github(file_path, json_data, commit_message="Update JSON file"):
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/contents/{file_path}'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    
    # Get the current content of the file (if it exists) to fetch its SHA
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        file_info = response.json()
        sha = file_info['sha']
        encoded_content = b64encode(json.dumps(json_data).encode()).decode()  # Encoding the JSON content
        
        # Update the file with new content
        data = {
            "message": commit_message,
            "content": encoded_content,
            "sha": sha
        }
    elif response.status_code == 404:
        # If the file doesn't exist, create it
        encoded_content = b64encode(json.dumps(json_data).encode()).decode()  # Encoding the JSON content
        data = {
            "message": commit_message,
            "content": encoded_content
        }
    else:
        print(f"Failed to get file content: {response.text}")
        return
    
    # Commit the new or updated content
    response = requests.put(url, json=data, headers=headers)
    
    if response.status_code == 201 or response.status_code == 200:
        print(f"File committed successfully: {file_path}")
    else:
        print(f"Failed to commit the file: {response.text}")


#-----------------------------------------------------------------------------#
def fetch_workflow_run_details(run_id):
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)

    status = None 
    if response.status_code == 200:
        workflow_run = response.json()
        name = workflow_run['name']
        status = workflow_run['status']
        conclusion = workflow_run['conclusion'] 
        display_title = workflow_run['display_title']
        print(f"[fetch_workflow_run_details] '{name}' '{status}' '{conclusion}' '{display_title}' ") 
        return status

    print(f"[fetch_workflow_run_details] Failed to fetch run details: {response.text}")
    return status


#-----------------------------------------------------------------------------#
def trigger_github_workflow(workflow_file):
    url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{workflow_file}/dispatches'
    runs_url = f'https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/workflows/{workflow_file}/runs'
    print(f"[trigger_github_workflow] url:'{url}' ")

    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    
    pre_trigger_runs = get_workflow_runs(runs_url, headers)
    
    payload = {"ref": "main"}
    response = requests.post(url, json=payload, headers=headers)
    
    if response.status_code == 201 or response.status_code == 204:
        print("[trigger_github_workflow] Workflow triggered successfully.")
        
        time.sleep(3)  
        run_id = wait_for_new_run(runs_url, headers, pre_trigger_runs)
        
        if run_id:
            print(f"[trigger_github_workflow] Workflow triggered with run ID: {run_id}")
            return run_id
        else:
            print("[trigger_github_workflow] No new workflow run found.")
            return None
    else:
        print(f"[trigger_github_workflow] Failed to trigger workflow: {response.text}")
        return None


def get_workflow_runs(runs_url, headers):
    response = requests.get(runs_url, headers=headers)
    if response.status_code == 200:
        runs = response.json()
        return [run['id'] for run in runs['workflow_runs']] 
    else:
        print(f"Failed to get workflow runs: {response.text}")
        return []


def wait_for_new_run(runs_url, headers, pre_trigger_runs):
    while True:
        current_runs = get_workflow_runs(runs_url, headers)
        new_runs = [run for run in current_runs if run not in pre_trigger_runs]
        
        if new_runs:
            return new_runs[0]  # Return the new run ID
        
        time.sleep(3)  # Adjust the sleep time as needed


#-----------------------------------------------------------------------------#
def download_artifact(run_id, artifact_name):
    # Define the base URL for GitHub API
    base_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}/artifacts"

    # Get the list of artifacts for the run
    response = requests.get(base_url, headers=headers)
    response.raise_for_status()
    
    artifacts = response.json().get('artifacts', [])
    
    # Find the artifact by name
    artifact = next((a for a in artifacts if a['name'] == artifact_name), None)
    
    if not artifact:
        #raise ValueError(f"Artifact '{artifact_name}' not found for run ID {run_id}.")
        print(f"Artifact '{artifact_name}' not found for run ID {run_id}.")
        return 
    
    # Download the artifact
    download_url = artifact['archive_download_url']
    download_response = requests.get(download_url, headers=headers, stream=True)
    download_response.raise_for_status()
    
    """
    with zipfile.ZipFile(io.BytesIO(download_response.raw.read()), 'r') as z:
        z.extractall(extract_to)
    
    print(f"Artifact '{artifact_name}' downloaded and extracted to '{extract_to}'.")
    """ 
    return io.BytesIO(download_response.raw.read()) 


def check_run_status(run_id) :
    if run_id is None : return False 

    run_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/runs/{run_id}"
    
    response = requests.get(run_url, headers=headers)
    response.raise_for_status()
    
    run_data = response.json()
    return run_data['status'] == 'completed' and run_data['conclusion'] == 'success'


def extract_artifact(artifact_name, artifact_zip, extract_to) : 
    if artifact_zip is None : return 
    
    with zipfile.ZipFile(artifact_zip, 'r') as z:
        z.extractall(extract_to)
    
    print(f"Artifact '{artifact_name}' downloaded and extracted to '{extract_to}'.")



#-----------------------------------------------------------------------------#
#-----------------------------------------------------------------------------#

check_github_connection() 


#json_data = {    "name": "John",    "age": 30,    "city": "New York"}
#commit_json_to_github('data/example.json', json_data, commit_message="Added example JSON data")
