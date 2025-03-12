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
request_count = 0  # Contador de peticiones

# Fecha límite (evitar commits muy antiguos)
now_date = datetime.now().isoformat() + 'Z'  # Fecha actual
until_date = datetime(2018, 1, 1)

def request_with_retry(url, headers, timeout=30):
    attempt = 0
    while True:
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()  # Esto levantará una excepción si la respuesta es un error HTTP
            return response
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            attempt += 1
            print(f"Error de conexión (intento {attempt}): {e}")
            time.sleep(5)  # Esperar 5 segundos antes de reintentar
        except requests.exceptions.RequestException as e:
            print(f"Error de solicitud: {e}")
            raise  # Levanta cualquier otro error

def get_rate_limit():
    """Obtiene el estado actual del rate limit desde la API de GitHub."""
    r = request_with_retry("https://api.github.com/rate_limit", headers)
    rate_data = r.json()
    remaining = rate_data['rate']['remaining']
    reset_time = rate_data['rate']['reset']
    reset_datetime = datetime.fromtimestamp(reset_time).strftime('%Y-%m-%d %H:%M:%S')
    return remaining, reset_time, reset_datetime

def check_rate_limit():
    """Verifica el rate limit y espera si es necesario."""
    global request_count
    remaining, reset_time, reset_datetime = get_rate_limit()
    time_until_reset = reset_time - int(time.time())
    
    print(f"Rate limit restante: {remaining} solicitudes. Reset en: {reset_datetime} ({time_until_reset} segundos)")
    
    if remaining <= 10:  # Si quedan pocas solicitudes, esperar
        wait_time = time_until_reset + 5  # 5s de margen
        print(f"Rate limit alcanzado. Esperando {wait_time} segundos...")
        time.sleep(wait_time)
        request_count = 0  # Reiniciar el contador

# Bucle principal para obtener commits
stop_fetching = False

while not stop_fetching:
    check_rate_limit()  # Verificar rate limit antes de cada petición

    url = repos_url.format(user, project, page, per_page, now_date)
    print(f"Fetching page {page}: {url}")

    r = request_with_retry(url, headers)
    request_count += 1

    if r.status_code != 200:
        print(f"Error: {r.status_code}, {r.text}")
        break

    commits_dict = r.json()
    if not commits_dict:
        print("No more commits found.")
        break

    bulk_operations = []  # Para operaciones en bloque de MongoDB
    processed_commits = 0

    for commit in commits_dict:
        commit_sha = commit['sha']
        commit_date = commit['commit']['committer']['date']
        commit_datetime = datetime.strptime(commit_date, "%Y-%m-%dT%H:%M:%SZ")

        if commit_datetime < until_date:
            print(f"Reached commit before the last one: {commit_sha} - {commit_date}")
            stop_fetching = True
            break

        # Verificar si el commit ya está almacenado con detalles
        existing_commit = collCommits.find_one(
            {"sha": commit_sha}, {"_id": 1, "modified_files": 1, "change_stats": 1}
        )

        if existing_commit and "modified_files" in existing_commit and "change_stats" in existing_commit:
            print(f"Skipping already stored commit: {commit_sha}")
            continue  # Evitar descargar detalles otra vez

        # Obtener detalles extendidos
        check_rate_limit()
        detailed_url = commit_url.format(user, project, commit_sha)
        detailed_commit_response = request_with_retry(detailed_url, headers)
        request_count += 1
        detailed_commit = detailed_commit_response.json()

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

        # Agregar operación en lote para mejorar rendimiento
        bulk_operations.append(
            pymongo.UpdateOne(
                {"sha": commit_sha},  # Buscar por SHA
                {"$set": commit},  # Insertar o actualizar
                upsert=True  # Evita insertar duplicados
            )
        )
        processed_commits += 1

    # Ejecutar operaciones en lote para acelerar la escritura en MongoDB
    if bulk_operations:
        collCommits.bulk_write(bulk_operations)

    total_commits += processed_commits
    print(f"Processed {processed_commits} commits on page {page}. Total processed: {total_commits}")

    if not stop_fetching:
        page += 1  # Pasar a la siguiente página

print(f"Total commits stored: {total_commits}")
