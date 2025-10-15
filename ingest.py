"""ingest.py — handles data loading and indexing from your GitHub repository"""

import os
from minsearch import Index
from sentence_transformers import SentenceTransformer

def load_repository_files(base_path: str = ".", exclude_dirs=("application", ".git", "__pycache__")):
    """Recursively load all .py, .md, and .txt files from repo."""
    documents = []
    for root, dirs, files in os.walk(base_path):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith((".py", ".md", ".txt")):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    documents.append({"filename": file, "path": path, "content": content})
                except Exception as e:
                    print(f"⚠️ Skipping {path}: {e}")
    return documents


def index_data(repo_owner: str, repo_name: str, filter=None):
    """Create a searchable hybrid index of your repo."""
    model = SentenceTransformer("all-MiniLM-L6-v2")

    docs = load_repository_files(".")
    if filter:
        docs = [d for d in docs if filter(d)]

    print(f"📚 Loaded {len(docs)} files from {repo_name} for indexing...")

    index = Index(docs)

    index.fit(docs)
    print("✅ Index built successfully!")
    return index
