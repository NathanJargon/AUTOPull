import os
import requests
from dotenv import load_dotenv
import time
from tenacity import retry, stop_after_attempt, wait_fixed

load_dotenv()

email = os.getenv('GITHUB_EMAIL')
username = os.getenv('REPO_OWNER')
repo = os.getenv('REPO_NAME')
token = os.getenv('GITHUB_TOKEN')

create_file_url = f"https://api.github.com/repos/{username}/{repo}/contents/new_file.txt"
pull_url = f"https://api.github.com/repos/{username}/{repo}/pulls"
merge_url = f"https://api.github.com/repos/{username}/{repo}/merges"
create_branch_url = f"https://api.github.com/repos/{username}/{repo}/git/refs"
list_files_url = f"https://api.github.com/repos/{username}/{repo}/contents"

headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
}

x, y = 700, 710

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def make_request(method, url, **kwargs):
    response = requests.request(method, url, headers=headers, **kwargs)
    response.raise_for_status()
    return response

def auto_create_file_pull_and_merge():
    try:
        for i in range(x, y):
            branch_name = f'new-branch-{i}'
            file_name = f'new_file_{i}.txt'
            create_file_url = f"https://api.github.com/repos/{username}/{repo}/contents/{file_name}"

            response = make_request('GET', f"https://api.github.com/repos/{username}/{repo}/git/refs/heads/main")
            sha = response.json()['object']['sha']

            branch_data = {
                'ref': f'refs/heads/{branch_name}',
                'sha': sha
            }
            make_request('POST', create_branch_url, json=branch_data)

            file_data = {
                'message': f'Create {file_name}',
                'content': 'SGVsbG8gd29ybGQ=', 
                'branch': branch_name,
            }
            make_request('PUT', create_file_url, json=file_data)

            pull_data = {
                'title': f'Auto pull request {i}',
                'head': branch_name, 
                'base': 'main',  
            }
            response = make_request('POST', pull_url, json=pull_data)
            pull_request = response.json()

            merge_data = {
                'base': pull_request['base']['ref'],
                'head': pull_request['head']['ref'],
                'commit_message': f"Auto-merging pull request #{pull_request['number']}",
            }
            make_request('POST', merge_url, json=merge_data)
            print(f"Merged pull request #{pull_request['number']}.")
    except Exception as e:
        print(f"Error occurred: {e}")
        delete_all_txt_files()

def delete_files():
    for i in range(x, y):
        file_name = f'new_file_{i}.txt'
        delete_file_url = f"https://api.github.com/repos/{username}/{repo}/contents/{file_name}"

        response = make_request('GET', delete_file_url)
        file_sha = response.json()['sha']
        file_path = response.json()['path']

        delete_data = {
            'message': f'Delete {file_name}',
            'sha': file_sha,
            'branch': 'main',
        }
        make_request('DELETE', delete_file_url, json=delete_data)
        print(f"Deleted file {file_name}.")

def delete_all_txt_files():
    response = make_request('GET', list_files_url)
    files = response.json()
    for file in files:
        if file['name'].endswith('.txt'):
            delete_file_url = f"https://api.github.com/repos/{username}/{repo}/contents/{file['path']}"
            response = make_request('GET', delete_file_url)
            file_sha = response.json()['sha']
            delete_data = {
                'message': f'Delete {file["name"]}',
                'sha': file_sha,
                'branch': 'main',
            }
            make_request('DELETE', delete_file_url, json=delete_data)
            print(f"Deleted file {file['name']}.")

auto_create_file_pull_and_merge()
time.sleep(1)
delete_files()