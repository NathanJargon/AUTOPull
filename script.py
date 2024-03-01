import os
import requests
import base64
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

url = "https://api.github.com/repos/{owner}/{repo}/contents/{path}"

email = os.getenv('GITHUB_EMAIL')
username = os.getenv('REPO_OWNER')
repo = os.getenv('REPO_NAME')
path = 'your_file.txt'  

token = os.getenv('GITHUB_TOKEN')
