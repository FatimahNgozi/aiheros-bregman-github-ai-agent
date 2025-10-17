"""ingest.py — Fetch and index GitHub repository content for search."""

import os
import requests
from dotenv import load_dotenv
from minsearch import Index

# --- Load environment variables ---
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# --- Helper: fetch repository files recursively ---
def get_repo_files_recursive(owner, repo, path="", token=None):
    """Recursively list files from a GitHub repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"
    headers = {"Authorization": f"token {token}"} if token else {}

    response = requests.get(url, headers=headers)
    if response.status_code == 403:
        raise Exception(
            f"GitHub API rate limit exceeded. Use a valid GITHUB_TOKEN in your .env file."
        )
    elif response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code} - {response.text}")

    items = response.json()
    files = []
    for item in items:
        if item["type"] == "file":
            files.append(item)
        elif item["type"] == "dir":
            files += get_repo_files_recursive(owner, repo, item["path"], token)
    return files


# --- Helper: download file content ---
def download_file_content(file_url, token=None):
    headers = {"Authorization": f"token {token}"} if token else {}
    response = requests.get(file_url, headers=headers)
    if response.status_code == 200:
        return response.text
    return None


# --- Main indexing function ---
def index_data(repo_owner: str, repo_name: str, file_filter=None):
    """
    Downloads, filters, and indexes files from a GitHub repo.
    Returns a MinSearch Index for semantic + keyword search.
    """
    print(f"📥 Fetching repository: {repo_owner}/{repo_name}")
    token = GITHUB_TOKEN

    files = get_repo_files_recursive(repo_owner, repo_name, token=token)
    print(f"✅ Retrieved {len(files)} files from GitHub")

    docs = []
    for f in files:
        filename = f["name"].lower()

        # Skip irrelevant files
        if not (filename.endswith(".md") or filename.endswith(".py") or filename.endswith(".yaml")):
            continue

        # Apply user filter if defined
        if file_filter and not file_filter(f):
            continue

        content = download_file_content(f["download_url"], token)
        if not content:
            continue

        docs.append({
            "filename": f["path"],
            "text": content,
            "url": f["html_url"]
        })

    print(f"📄 Indexed {len(docs)} documents")

# Create a MinSearch index
    index = Index(text_fields=["path", "content"])
    index.fit(docs)


    print("✅ Index created successfully!")
    return index
