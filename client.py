import requests
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

token = os.getenv('GITHUB_TOKEN')
if not token:
    raise ValueError("No GITHUB_TOKEN found in environment variables")

headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json'
}
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_NAME = 'github'
COLLECTION_COMMITS = 'commits'
connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
collCommits = connection[DB_NAME][COLLECTION_COMMITS]

repos_url = 'https://api.github.com/repos/{}/{}/commits?page={}&per_page={}'
'https://github.com/sourcegraph/sourcegraph-public-snapshot/commits/'

user = 'microsoft'
project = 'vscode'
per_page = 100
page = 1
total_commits = 0
max_commits = 1000

# Definir la fecha mínima (1 de enero de 2018)
start_data = datetime(2018, 1, 1)

while total_commits < max_commits:
    url = repos_url.format(user, project, page, per_page)
    r = requests.get(url, headers=headers)
    commits_dict = r.json()
    if not commits_dict:
        break
    for commit in commits_dict:
        commit_date_str = commit['commit']['commiter']['date'] # Fecha del commit en string
        commit_date = datetime.strptime(commit_date-str, '%Y-%m-%dT%H:%M:%SZ') # Convertir a objeto datetime
        
        commit['projectId'] = project
        # print(str(commit))
        collCommits.insert_one(commit)
        total_commits += 1
        if total_commits >= max_commits:
            break
    page += 1