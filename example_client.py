import requests
import pymongo
from pymongo import MongoClient
token = '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'
headers = {
    "Authorization": f"token {token}",
    "Accept": "application/vnd.github.v3+json"
}
MONGODB_HOST = 'localhost'
MONGODB_PORT = 27017
DB_NAME = 'github'
COLLECTION_COMMITS = 'commits'
connection = MongoClient(MONGODB_HOST, MONGODB_PORT)
collCommits = connection[DB_NAME][COLLECTION_COMMITS]

repos_url = 'https://api.github.com/repos/{}/{}/commits?page={}&per_page={}'

user = 'microsoft'
project = 'vscode'

url = repos_url.format(user, project, 1, 1)
r = requests.get(url, headers=headers)
commits_dict = r.json()

for commit in commits_dict:
    commit['projectId'] = project;
    print(str(commit))
    collCommits.insert_one(commit)