import requests
import os
import time
from minsearch import Index
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
RAW_BASE = "https://raw.githubusercontent.com"


def list_repo_files(owner, repo):
    """
    Get all .md files in the GitHub repo.
    Uses GitHub’s tree API once, then reads from raw.githubusercontent.com.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    print("🔍 Fetching file tree...")
    response = requests.get(url, headers=headers)

    if response.status_code == 403 and "API rate limit" in response.text:
        raise Exception("⚠️ GitHub API rate limit exceeded — please add or update your GITHUB_TOKEN in .env.")
    elif response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code} - {response.text}")

    tree = response.json().get("tree", [])
    return [item["path"] for item in tree if item["path"].endswith(".md")]


def get_file_content(owner, repo, path, retries=3, delay=2):
    """Fetch markdown file directly from raw.githubusercontent.com (with retry)."""
    url = f"{RAW_BASE}/{owner}/{repo}/master/{path}"

    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                print(f"⚠️ Skipping {path} (HTTP {response.status_code})")
                return ""
        except requests.exceptions.RequestException as e:
            print(f"Retry {attempt + 1}/{retries} for {path} due to error: {e}")
            time.sleep(delay)

    return ""


def index_data(repo_owner, repo_name):
    """Fetch all markdown files and build a Minsearch index."""
    print(f"📂 Fetching files from {repo_owner}/{repo_name} ...")
    files = list_repo_files(repo_owner, repo_name)

    docs = []
    for path in files:
        content = get_file_content(repo_owner, repo_name, path)
        if content.strip():
            docs.append({
                "id": path,
                "filename": os.path.basename(path),
                "text": content
            })

    print(f"✅ Indexed {len(docs)} markdown files.")

    # ✅ FIX: Pass arguments positionally to avoid the 'multiple values' error
    index = Index(docs, ["text", "filename"], ["id"])
    return index

