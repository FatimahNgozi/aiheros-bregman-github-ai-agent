import requests
import os
from dotenv import load_dotenv

# If minsearch fails import, we’ll handle that too
try:
    from minsearch import Index
except ImportError:
    raise ImportError("⚠️ The 'minsearch' library is not installed. Run 'pip install minsearch'.")

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
RAW_BASE = "https://raw.githubusercontent.com"


def list_repo_files(owner, repo):
    """List all markdown files in the repo using GitHub tree API."""
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
    """Fetch file directly from raw.githubusercontent.com."""
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

    # ✅ Correct for minsearch 0.0.7
    index = Index(
        text_fields=["text", "filename"],
        keyword_fields=["id"]
    )
    index.fit(docs)

    return index
