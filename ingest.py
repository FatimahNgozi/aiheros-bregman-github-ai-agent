# application/ingest.py
from minsearch import Index
import requests

def index_data(repo_owner: str, repo_name: str, filter=None):
    """Fetch repository content and build searchable index."""

    # Example docs loader — you can adapt to your own GitHub content structure
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents"
    response = requests.get(url)
    files = response.json()

    docs = []
    for f in files:
        if not f["name"].endswith(".md"):
            continue

        if filter and not filter(f):
            continue

        # Download content
        raw = requests.get(f["download_url"]).text
        docs.append({
            "filename": f["name"],
            "content": raw,
            "keywords": f["name"].split("_")
        })

    # ✅ Correct Index initialization
    index = Index(
        text_fields=["content"],
        keyword_fields=["keywords"]
    )

    # ✅ Fit the index with documents
    index.fit(docs)

    return index

