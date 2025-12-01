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


# ---- FIXED UNIVERSAL SEARCH WRAPPER ---- #

def resolve_results(raw, index_obj):
    docs = index_obj._docs

    # Case 1: [3, 10, 5]
    if raw and isinstance(raw[0], int):
        return [docs[i] for i in raw]

    # Case 2: [(3, 0.89), (10, 0.74)]
    if raw and isinstance(raw[0], (list, tuple)) and len(raw[0]) == 2:
        return [docs[i] for (i, score) in raw]

    # Case 3: Already dicts
    if raw and isinstance(raw[0], dict):
        return raw

    return []


if query:
    try:
        raw = index.search(query, {"text": 1}, 3)   # valid for ALL versions
        results = resolve_results(raw, index)

        if not results:
            st.warning("No results found.")

        for r in results:
            st.subheader(r["filename"])
            st.caption(r["id"])
            st.write(r["text"][:600] + "…")
            st.markdown("---")

    except Exception as e:
        st.error(f"❌ Search error: {e}")

