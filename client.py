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

# Configuración de mongoDB
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_NAME = 'github'
COLLECTION_COMMITS = 'commits'
connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
collCommits = connection[DB_NAME][COLLECTION_COMMITS]

repos_url = 'https://api.github.com/repos/{}/{}/commits?page={}&per_page={}'
'https://github.com/sourcegraph/sourcegraph-public-snapshot/commits/'

# Configuración del repositorio y fechas
user = 'microsoft'
project = 'vscode'
per_page = 100
page = 1
total_commits = 0

# Rango de fechas
since_date = datetime(2018, 1, 1).isoformat() + 'Z'
until_date = datetime.now().isoformat() + 'Z' # Fecha actual


while True:
    url = repos_url.format(user, project, page, per_page, since_date, until_date)
    print(f"Fetching page {page}: {url}")
    r = requests.get(url, headers=headers)
    
    if r.status_code != 200:
        print(f"Error: {r.status_code}, {r.text}")
        break # Salir si hay error
    
    for commit in commits_dict:
        commit['projectId'] = project
        # print(str(commit))
        collCommits.insert_one(commit)
        total_commits += 1
        if total_commits >= max_commits:
            break
    page += 1