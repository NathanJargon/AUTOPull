import os
import requests
from dotenv import load_dotenv

load_dotenv()

email = os.getenv('GITHUB_EMAIL')
username = os.getenv('REPO_OWNER')
repo = os.getenv('REPO_NAME')
token = os.getenv('GITHUB_TOKEN')

create_file_url = f"https://api.github.com/repos/{username}/{repo}/contents/new_file.txt"
pull_url = f"https://api.github.com/repos/{username}/{repo}/pulls"
merge_url = f"https://api.github.com/repos/{username}/{repo}/merges"
create_branch_url = f"https://api.github.com/repos/{username}/{repo}/git/refs"

headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
}

def auto_create_file_pull_and_merge():
    for i in range(10):
        branch_name = f'new-branch-{i}'
        file_name = f'new_file_{i}.txt'
        create_file_url = f"https://api.github.com/repos/{username}/{repo}/contents/{file_name}"

        response = requests.get(f"https://api.github.com/repos/{username}/{repo}/git/refs/heads/main", headers=headers)
        response.raise_for_status()
        sha = response.json()['object']['sha']

        branch_data = {
            'ref': f'refs/heads/{branch_name}',
            'sha': sha
        }
        response = requests.post(create_branch_url, headers=headers, json=branch_data)
        response.raise_for_status()

        file_data = {
            'message': f'Create {file_name}',
            'content': 'SGVsbG8gd29ybGQ=', 
            'branch': branch_name,
        }
        response = requests.put(create_file_url, headers=headers, json=file_data)
        response.raise_for_status()

        pull_data = {
            'title': f'Auto pull request {i}',
            'head': branch_name, 
            'base': 'main',  
        }
        response = requests.post(pull_url, headers=headers, json=pull_data)
        response.raise_for_status()
        pull_request = response.json()

        merge_data = {
            'base': pull_request['base']['ref'],
            'head': pull_request['head']['ref'],
            'commit_message': f"Auto-merging pull request #{pull_request['number']}",
        }
        response = requests.post(merge_url, headers=headers, json=merge_data)
        response.raise_for_status()
        print(f"Merged pull request #{pull_request['number']}.")

def delete_files():
    for i in range(10):
        file_name = f'new_file_{i}.txt'
        delete_file_url = f"https://api.github.com/repos/{username}/{repo}/contents/{file_name}"

        # First, we need to get the file to find its SHA and path
        response = requests.get(delete_file_url, headers=headers)
        response.raise_for_status()
        file_sha = response.json()['sha']
        file_path = response.json()['path']

        delete_data = {
            'message': f'Delete {file_name}',
            'sha': file_sha,
            'branch': 'main',
        }
        response = requests.delete(delete_file_url, headers=headers, json=delete_data)
        response.raise_for_status()
        print(f"Deleted file {file_name}.")
        
   
delete_files()    
# auto_create_file_pull_and_merge()