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

# Función para verificar el rate limit
def check_rate_limit(headers):
    remaining = int(headers.get('X-RateLimit-Remaining', 0))
    reset_time = int(headers.get('X-RateLimit-Reset', 0))

    # Comprobar si el valor de reset_time es negativo
    current_time = int(time.time())  # Tiempo actual en segundos desde la época Unix
    if remaining == 0:
        # Calcular cuánto tiempo queda hasta que se restablezca el rate limit
        reset_time = reset_time - current_time
        if reset_time < 0:
            reset_time = 0  # Si el tiempo de espera es negativo, no dormir
        print(f"Rate limit alcanzado. Esperando {reset_time} segundos...")
        time.sleep(reset_time)  # Dormir el tiempo calculado
    else:
        print(f"Rate limit restante: {remaining} solicitudes.")

headers = {
    'Authorization': f'token {token}',
    'Accept': 'application/vnd.github.v3+json'
}

# Conexión con MongoDB
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

# Verificar el rate limit antes de hacer solicitudes
rate_limit_url = 'https://api.github.com/rate_limit'
r = requests.get(rate_limit_url, headers=headers)
if r.status_code == 200:
    rate_limit_data = r.json()
    check_rate_limit(rate_limit_data['resources']['core'])
else:
    print(f"Error al comprobar el rate limit: {r.status_code}")
    exit(1)

# Ciclo para obtener los commits
while total_commits < max_commits:
    url = repos_url.format(user, project, page, per_page)
    r = requests.get(url, headers=headers)
    
    # Verificar rate limit después de cada solicitud
    check_rate_limit(r.headers)
    
    commits_dict = r.json()
    if not commits_dict:
        break
    for commit in commits_dict:
        commit['projectId'] = project
        collCommits.insert_one(commit)
        total_commits += 1
        if total_commits >= max_commits:
            break
    page += 1
