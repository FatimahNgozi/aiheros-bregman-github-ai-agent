import requests
import os
from minsearch import Index
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
RAW_BASE = "https://raw.githubusercontent.com"


def list_repo_files(owner, repo):
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1"
    headers = {"Accept": "application/vnd.github.v3+json"}

    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    res = requests.get(url, headers=headers)
    data = res.json()

    return [f["path"] for f in data.get("tree", []) if f["path"].endswith(".md")]


def get_file_content(owner, repo, path):
    url = f"{RAW_BASE}/{owner}/{repo}/master/{path}"
    res = requests.get(url)
    return res.text if res.status_code == 200 else ""


def index_data(owner, repo):
    files = list_repo_files(owner, repo)

    docs = []
    for p in files:
        content = get_file_content(owner, repo, p)
        if content.strip():
            docs.append({
                "id": p,
                "filename": os.path.basename(p),
                "text": content
            })

    index = Index(
        text_fields=["text"],
        keyword_fields=["filename", "id"],
    )

    index.fit(docs)
    index._docs = docs  # store original docs for safe lookup

    return index

