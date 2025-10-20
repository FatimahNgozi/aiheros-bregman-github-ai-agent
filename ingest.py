import requests
import os
from minsearch import Index
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
RAW_BASE = "https://raw.githubusercontent.com"

def list_repo_files(owner, repo):
    """
    Get all .md files in the GitHub repo using the public raw file tree.
    This uses GitHub’s public tree API once, then downloads from raw.githubusercontent.com
    (which avoids the API rate limit issue entirely).
    """
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
    """Fetch markdown file directly from raw.githubusercontent.com (no API)."""
    url = f"{RAW_BASE}/{owner}/{repo}/master/{path}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print(f"⚠️ Could not fetch {path} (HTTP {response.status_code})")
        return ""


def index_data(repo_owner, repo_name):
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

    index = Index(
        docs,
        text_fields=["text", "filename"],
        keyword_fields=["id"]
    )

    return index

