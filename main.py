import streamlit as st
from application import ingest

REPO_OWNER = "bregman-arie"
REPO_NAME = "devops-exercises"

@st.cache_resource
def load_index():
    return ingest.index_data(REPO_OWNER, REPO_NAME)

st.set_page_config(page_title="DevOps AI Agent")
st.title("🤖 DevOps Exercises Search Agent")

index = load_index()

query = st.text_input("Ask a question:")

# -------------------------------
# 🔥 UNIVERSAL SAFE SEARCH PARSER
# -------------------------------
def safe_search(index_obj, query, limit=3):
    raw = index_obj.search(query, {"text": 1}, limit)
    docs = index_obj._docs

    safe_results = []

    for item in raw:
        # Case: "item" is an integer ID → convert to doc
        if isinstance(item, int):
            if 0 <= item < len(docs):
                safe_results.append(docs[item])
            continue

        # Case: "item" is (id, score) → extract id
        if isinstance(item, (list, tuple)) and len(item) == 2:
            idx = item[0]
            if isinstance(idx, int) and 0 <= idx < len(docs):
                safe_results.append(docs[idx])
            continue

        # Case: already dict → accept directly
        if isinstance(item, dict):
            safe_results.append(item)
            continue

    return safe_results


if query:
    try:
        results = safe_search(index, query, 3)

        if not results:
            st.warning("No results found.")

        for r in results:
            st.subheader(r["filename"])
            st.caption(r["id"])
            st.write(r["text"][:600] + "…")
            st.markdown("---")

    except Exception as e:
        st.error(f"❌ Search error: {e}")

