import requests
import os
import json
from minsearch import Index
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
RAW_BASE = "https://raw.githubusercontent.com"
CACHE_FILE = "index_cache.json"  # local cache file


def list_repo_files(owner, repo):
    """Fetch all .md files from GitHub repo tree."""
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
    md_files = [item["path"] for item in tree if item["path"].endswith(".md")]
    return md_files


def get_file_content(owner, repo, path):
    """Fetch markdown file content directly from raw.githubusercontent.com."""
    url = f"{RAW_BASE}/{owner}/{repo}/master/{path}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"⚠️ Skipping {path} (HTTP {response.status_code})")
        return ""


def load_cached_index():
    """Load cached docs from local JSON file if it exists."""
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"📦 Loaded {len(data)} cached documents from {CACHE_FILE}")
            return data
        except Exception as e:
            print(f"⚠️ Failed to load cache: {e}")
    return None


def save_cache(docs):
    """Save docs to cache file."""
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)
        print(f"✅ Saved {len(docs)} documents to cache ({CACHE_FILE})")
    except Exception as e:
        print(f"⚠️ Failed to save cache: {e}")


def index_data(repo_owner, repo_name, force_refresh=False):
    """Build (or load) the index."""
    if not force_refresh:
        cached_docs = load_cached_index()
        if cached_docs:
            print("💾 Using cached index (no API calls needed).")
            return Index(cached_docs, ["text", "filename"], ["id"])

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
    save_cache(docs)

    return Index(docs, ["text", "filename"], ["id"])

