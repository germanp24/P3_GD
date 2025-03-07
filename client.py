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

# Función para verificar el rate limit
def check_rate_limit(response_headers):
    remaining = int(response_headers.get('X-RateLimit-Remaining', 0))
    reset_time = int(response_headers.get('X-RateLimit-Reset', 0))
    
    current_time = int(time.time())
    if remaining == 0:
        wait_time = reset_time - current_time
        if wait_time > 0:
            print(f"Rate limit alcanzado. Esperando {wait_time} segundos...")
            time.sleep(wait_time)
    else:
        print(f"Rate limit restante: {remaining} solicitudes.")

# Configuración de MongoDB
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_NAME = 'github'
COLLECTION_COMMITS = 'commits'
connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
collCommits = connection[DB_NAME][COLLECTION_COMMITS]

repos_url = 'https://api.github.com/repos/{}/{}/commits?page={}&per_page={}'
commit_url = 'https://api.github.com/repos/{}/{}/commits/{}'

# Configuración del repositorio y fechas
user = 'microsoft'
project = 'vscode'
per_page = 100
page = 1
total_commits = 0

# Rango de fechas
now_date = datetime.now().isoformat() + 'Z'  # Fecha actual
until_date = datetime(2018, 1, 1)

stop_fetching = False

while not stop_fetching:
    url = repos_url.format(user, project, page, per_page, now_date)
    print(f"Fetching page {page}: {url}")
    
    r = requests.get(url, headers=headers)
    check_rate_limit(r.headers)  # Verificar el rate limit después de cada solicitud
    
    if r.status_code != 200:
        print(f"Error: {r.status_code}, {r.text}")
        break  # Salir si hay error
    
    commits_dict = r.json()
    
    if not commits_dict:
        print("No more commits found.")
        break
    
    for commit in commits_dict:
        commit_sha = commit['sha']
        commit_date = commit['commit']['committer']['date']
        commit_datetime = datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")

        if commit_datetime < until_date:
            print(f"Reached commit before the last one: {commit_sha} - {commit_date}")
            stop_fetching = True
            break
        
        # Verificar si ya existe en MongoDB con los campos extendidos
        existing_commit = collCommits.find_one(
            {"sha": commit_sha}, {"modified_files": 1, "change_stats": 1}
        )
        
        if existing_commit and "modified_files" in existing_commit and "change_stats" in existing_commit:
            print(f"Skipping already stored commit: {commit_sha}")
            continue

        # Obtener detalles extendidos de cada commit
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
        
        # Evitar insertar duplicados en MongoDB
        collCommits.update_one(
            {"sha": commit_sha},  # Buscar por SHA
            {"$set": commit},  # Insertar o actualizar
            upsert=True  # Evita insertar duplicados
        )

        total_commits += 1
        print(f"Found commit: {commit_sha} - {commit_date}")
        
    if not stop_fetching:
        page += 1  # Pasar a la siguiente página

print(f"Total commits found: {total_commits}")
