# AUTOPull :octocat:

This repository contains a Python script that automates the process of pulling and merging changes from a GitHub repository using the GitHub API.

## :gear: Setup & Usage

### Prerequisites

- Python 3.6+
- pip (Python package installer)

### Installation

1. Clone this repository and navigate into it:

```bash
git clone https://github.com/your_username/AUTOPull.git
cd AUTOPull
pip install python-dotenv requests schedule
```

2. Install the required Python packages:

```bash
pip install python-dotenv requests
```
    
### Configuration

Create a `.env` file in the root directory of the project and add the following environment variables:

```bash
REPO_OWNER=your_username
REPO_NAME=your_repository
GITHUB_TOKEN=your_personal_access_token
GITHUB_EMAIL=your_github_email
```

### Running the Script

Execute the script using Python:

```bash
python script.py
```

## :warning: Warning

- The script will pull and merge changes in the specified repository according to the schedule. Use this script with caution, as merging changes cannot be undone through the API.

- Making a large number of commits in a short period of time might be considered abuse of the GitHub API and could potentially lead to your account being flagged or rate-limited. Use the script responsibly and only make commits as needed.

## :handshake: Contributing

Contributions, issues, and feature requests are welcome! Feel free to check [issues page](https://github.com/NathanJargon/AUTOPull/issues).