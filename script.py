import os
import requests
from dotenv import load_dotenv
import time
from tenacity import retry, stop_after_attempt, wait_fixed

load_dotenv()

# Configuration
email = os.getenv('GITHUB_EMAIL')
username = os.getenv('REPO_OWNER')
repo = os.getenv('REPO_NAME')
token = os.getenv('GITHUB_TOKEN')

# URLs
base_url = f"https://api.github.com/repos/{username}/{repo}"
pull_url = f"{base_url}/pulls"
merge_url = f"{base_url}/merges"
create_branch_url = f"{base_url}/git/refs"
list_files_url = f"{base_url}/contents"

headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json',
}

def read_values():
    try:
        with open('values.txt', 'r') as file:
            return tuple(map(int, file.read().split()))
    except FileNotFoundError:
        return (0, 10)  # Default values

def write_values(x, y):
    with open('values.txt', 'w') as file:
        file.write(f"{x}\n{y}\n")

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def make_request(method, url, **kwargs):
    response = requests.request(method, url, headers=headers, **kwargs)
    response.raise_for_status()
    return response

def auto_create_file_pull_and_merge():
    global x, y
    try:
        for i in range(x, y):
            branch_name = f'new-branch-{i}'
            file_name = f'new_file_{i}.txt'
            file_url = f"{base_url}/contents/{file_name}"

            # Get main branch SHA
            response = make_request('GET', f"{base_url}/git/refs/heads/main")
            sha = response.json()['object']['sha']

            # Create branch
            make_request('POST', create_branch_url, json={
                'ref': f'refs/heads/{branch_name}',
                'sha': sha
            })

            # Create file
            make_request('PUT', file_url, json={
                'message': f'Create {file_name}',
                'content': 'SGVsbG8gd29ybGQ=',  # Base64 encoded "Hello world"
                'branch': branch_name,
            })

            # Create PR
            response = make_request('POST', pull_url, json={
                'title': f'Auto pull request {i}',
                'head': branch_name,
                'base': 'main',
            })
            pr = response.json()

            # Merge PR
            make_request('POST', merge_url, json={
                'base': pr['base']['ref'],
                'head': pr['head']['ref'],
                'commit_message': f"Merged PR #{pr['number']}",
            })
            print(f"Merged pull request #{pr['number']}")

        # Update values only if successful
        x += 10
        y += 10
        write_values(x, y)

    except Exception as e:
        print(f"Error: {str(e)}")
        delete_files(suppress_errors=True)  # Cleanup before retrying
        x += 10
        y += 10
        write_values(x, y)  # Ensure the loop does not retry the same values

def delete_files(suppress_errors=False):
    try:
        # List all files in the repository
        response = make_request('GET', list_files_url)
        files = response.json()

        for file in files:
            file_name = file['name']
            if file_name.startswith('new'):
                file_url = f"{base_url}/contents/{file_name}"

                try:
                    # Get file SHA
                    response = make_request('GET', file_url)
                    sha = response.json().get('sha')

                    if not sha:
                        print(f"Skipping deletion: {file_name} not found")
                        continue

                    # Delete file
                    make_request('DELETE', file_url, json={
                        'message': f'Delete {file_name}',
                        'sha': sha,
                        'branch': 'main',
                    })
                    print(f"Deleted {file_name}")

                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 404:
                        print(f"File {file_name} already removed or not found")
                    elif not suppress_errors:
                        raise

    except Exception as e:
        if not suppress_errors:
            raise
        print(f"Error during deletion: {str(e)}")

def main():
    global x, y
    x, y = read_values()
    
    try:
        auto_create_file_pull_and_merge()
        time.sleep(1)
        delete_files()
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        delete_files(suppress_errors=True)  # Ensure cleanup on fatal error
        write_values(x, y)  # Preserve current state

if __name__ == "__main__":
    main()