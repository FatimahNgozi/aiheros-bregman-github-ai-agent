# application/search_tools.py

from minsearch import Index

def hybrid_search(index: Index, query: str, top_k: int = 5):
    """Perform hybrid keyword + semantic search."""
    return index.search(query, top_k=top_k)
