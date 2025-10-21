import requests
import os
import json
from minsearch import Index
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
RAW_BASE = "https://raw.githubusercontent.com"
CACHE_FILE = "index_cache.json"


def list_repo_files(owner, repo):
    """List all Markdown files in the repo."""
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/master?recursive=1"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    response = requests.get(url, headers=headers)
    if response.status_code == 403 and "API rate limit" in response.text:
        raise Exception("⚠️ GitHub API rate limit exceeded — please add or update your GITHUB_TOKEN in .env.")
    elif response.status_code != 200:
        raise Exception(f"GitHub API error: {response.status_code} - {response.text}")

    tree = response.json().get("tree", [])
    return [item["path"] for item in tree if item["path"].endswith(".md")]


def get_file_content(owner, repo, path):
    """Fetch markdown content directly from raw.githubusercontent.com."""
    url = f"{RAW_BASE}/{owner}/{repo}/master/{path}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"⚠️ Could not fetch {path} (HTTP {response.status_code})")
        return ""


def index_data(repo_owner, repo_name, force_refresh=False):
    """Build or load cached index."""
    # ✅ Load from cache if available and not forcing refresh
    if not force_refresh and os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            docs = json.load(f)
        print("✅ Loaded index from cache.")
    else:
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

        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(docs, f, indent=2)

        print(f"✅ Indexed {len(docs)} markdown files and saved to cache.")

    # ✅ Build search indexindex = Index(
    index = Index(
    	text_fields=["text", "filename"],
    	keyword_fields=["id"]
    )

    index.fit(docs)


    return index

