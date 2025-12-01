import os
import time
import json
import pickle
import logging
from typing import List

import requests
from dotenv import load_dotenv
from minsearch import Index

load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
RAW_BASE = "https://raw.githubusercontent.com"
CACHE_DIR = os.getenv("INDEX_CACHE_DIR", ".cache")
CACHE_FILE = os.path.join(CACHE_DIR, "minsearch_index.pkl")
DOCS_FILE = os.path.join(CACHE_DIR, "docs.json")

# Retry settings
RETRY_BACKOFF = [0.5, 1.0, 2.0]


def _safe_get(url: str, headers: dict | None = None, timeout: int = 10) -> requests.Response:
    """GET with basic retry/backoff and simple SSL/connection handling."""
    headers = headers or {}
    for attempt, backoff in enumerate(RETRY_BACKOFF + [None]):
        try:
            resp = requests.get(url, headers=headers, timeout=timeout)
            resp.raise_for_status()
            return resp
        except requests.exceptions.SSLError as e:
            logger.warning("SSL error while fetching %s: %s", url, e)
            # small sleep and retry — some transient SSL issues disappear
        except requests.exceptions.RequestException as e:
            logger.warning("Request error while fetching %s: %s", url, e)
        if backoff is None:
            break
        time.sleep(backoff)
    raise Exception(f"Failed to GET {url} after retries")


def list_repo_files(owner: str, repo: str, branch: str = "master") -> List[str]:
    """Return list of .md file paths in repo via the git/trees API.
    Falls back to the contents API if necessary.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}?recursive=1"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"

    resp = _safe_get(url, headers=headers)
    data = resp.json()

    # If data contains 'tree' it's the list
    tree = data.get("tree") or []
    md_files = [item["path"] for item in tree if item.get("path", "").endswith(".md")]
    return md_files


def get_file_content(owner: str, repo: str, path: str, branch: str = "master") -> str:
    """Fetch file from raw.githubusercontent.com (no API) — safer for rate limits.
    """
    url = f"{RAW_BASE}/{owner}/{repo}/{branch}/{path}"
    resp = _safe_get(url)
    return resp.text


def _ensure_cache_dir():
    os.makedirs(CACHE_DIR, exist_ok=True)


def _sanitize_doc(doc: dict) -> dict:
    """Force all fields to strings — MinSearch expects strings for text fields.
    Keep only id, filename, text.
    """
    sanitized = {
        "id": str(doc.get("id", "")),
        "filename": str(doc.get("filename", "")),
        "text": str(doc.get("text", ""))
    }
    return sanitized


def index_data(repo_owner: str, repo_name: str, force_refresh: bool = False, branch: str = "master") -> Index:
    """Build or load a MinSearch index for the repository.

    - Uses raw.githubusercontent for file content to avoid hitting API rate limits.
    - Sanitizes docs to strings to avoid 'list' object has no attribute 'items' errors.
    - Caches built Index on disk (pickle) to avoid rebuilds.
    """
    _ensure_cache_dir()

    # Try load cached index
    if not force_refresh and os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "rb") as f:
                index = pickle.load(f)
            logger.info("Loaded index from cache: %s", CACHE_FILE)
            return index
        except Exception:
            logger.exception("Failed loading cached index, will rebuild")

    logger.info("Fetching repo file list for %s/%s", repo_owner, repo_name)
    files = list_repo_files(repo_owner, repo_name, branch=branch)

    docs = []
    for path in files:
        try:
            content = get_file_content(repo_owner, repo_name, path, branch=branch)
            if content and content.strip():
                docs.append({
                    "id": path,
                    "filename": os.path.basename(path),
                    "text": content
                })
        except Exception:
            logger.exception("Failed to fetch %s — skipping", path)

    # Sanitize all docs to ensure only strings
    docs = [_sanitize_doc(d) for d in docs]

    # Persist docs for debugging
    try:
        with open(DOCS_FILE, "w", encoding="utf-8") as f:
            json.dump(docs, f, ensure_ascii=False, indent=2)
    except Exception:
        logger.exception("Failed to persist docs.json (non-fatal)")

    # Build MinSearch index using the new API
    index = Index(text_fields=["text", "filename"], keyword_fields=["id"])
    index.fit(docs)

    # Cache the index object
    try:
        with open(CACHE_FILE, "wb") as f:
            pickle.dump(index, f)
        logger.info("Wrote index cache to %s", CACHE_FILE)
    except Exception:
        logger.exception("Failed to cache index (non-fatal)")

    return index


if __name__ == "__main__":
    # quick local test
    owner = os.getenv("DEVOPS_OWNER", "bregman-arie")
    repo = os.getenv("DEVOPS_REPO", "devops-exercises")
    idx = index_data(owner, repo, force_refresh=False)
    print("Indexed successfully")

