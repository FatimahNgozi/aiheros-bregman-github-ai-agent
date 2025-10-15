from minsearch import Index
import requests
import streamlit as st

def index_data(repo_owner: str, repo_name: str, filter=None):
    """Fetch repository content and build searchable index."""

    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents"
    response = requests.get(url)
    files = response.json()

    # ✅ Handle API errors
    if not isinstance(files, list):
        st.error(f"GitHub API error: {files.get('message', 'Unknown error')}")
        return None

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

    if not docs:
        st.warning("No markdown files found in the repo.")
        return None

    index = Index(
        text_fields=["content"],
        keyword_fields=["keywords"]
    )

    index.fit(docs)
    return index

