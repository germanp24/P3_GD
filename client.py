import requests
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
import time

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
commit_url = 'https://api.github.com/repos/{}/{}/commits/{}'

user = 'microsoft'
project = 'vscode'
per_page = 100
page = 1
total_commits = 0
max_commits = 1000

# Definir la fecha mínima (1 de enero de 2018)
start_date = datetime(2018, 1, 1)

while total_commits < max_commits:
    url = repos_url.format(user, project, page, per_page)
    r = requests.get(url, headers=headers)
    
    # Comprobar rate limit
    if r.status_code == 403 and 'X-RateLimit-Reset' in r.headers:
        reset_time = int(r.headers['X-RateLimit-Reset'])
        wait_time = max(0, reset_time - int(time.time())) + 5  # Esperar con margen
        print(f"Rate limit alcanzado. Esperando {wait_time} segundos...")
        time.sleep(wait_time)
        continue

    commits_dict = r.json()
    if not commits_dict:
        break

    for commit in commits_dict:
        # Obtener detalles extendidos de cada commit
        commit_sha = commit['sha']
        detailed_url = commit_url.format(user, project, commit_sha)
        detailed_response = requests.get(detailed_url, headers=headers)
        detailed_commit = detailed_response.json()

        # Extraer archivos modificados y estadísticas de cambios
        modified_files = [file['filename'] for file in detailed_commit.get('files', [])]
        change_stats = {
            'additions': sum(file.get('additions', 0) for file in detailed_commit.get('files', [])),
            'deletions': sum(file.get('deletions', 0) for file in detailed_commit.get('files', [])),
            'total': sum(file.get('changes', 0) for file in detailed_commit.get('files', []))
        }

        # Añadir campos extendidos
        commit['projectId'] = project
        commit['modified_files'] = modified_files
        commit['change_stats'] = change_stats

        # Insertar en MongoDB
        collCommits.insert_one(commit)
        total_commits += 1

        if total_commits >= max_commits:
            break

    page += 1
