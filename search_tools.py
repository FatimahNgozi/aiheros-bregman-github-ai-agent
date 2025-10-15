"""search_tools.py — hybrid keyword + semantic search logic"""

from minsearch import Index

def hybrid_search(index: Index, query: str, top_k: int = 5):
    """Perform hybrid keyword + semantic search over repo docs."""
    results = index.search(query, top_k=top_k)
    formatted = []
    for r in results:
        formatted.append({
            "filename": r.get("filename"),
            "score": r.get("score"),
            "content": r.get("content")[:500] + "..."  # preview
        })
    return formatted
