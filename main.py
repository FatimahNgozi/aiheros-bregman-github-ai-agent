import streamlit as st
from application import ingest

REPO_OWNER = "bregman-arie"
REPO_NAME = "devops-exercises"

st.set_page_config(page_title="DevOps Exercises AI Agent", layout="wide")
st.title("🤖 DevOps Exercises Search Agent")
st.write("Search the DevOps Exercises repository (markdown files) using a local index.")

# Provide a control to force rebuild the index
with st.sidebar:
    st.header("Index")
    force = st.button("🔄 Force rebuild index")
    st.markdown("If you recently changed the repo or .env (GITHUB_TOKEN), click refresh.")

@st.cache_resource
def load_index(force_refresh: bool = False):
    return ingest.index_data(REPO_OWNER, REPO_NAME, force_refresh=force_refresh)

with st.spinner("Building or loading index..."):
    index = load_index(force_refresh=force)

if index is None:
    st.error("Failed to build index — check logs and ensure GITHUB_TOKEN (if private repo) is set.")
    st.stop()

query = st.text_input("Ask a question about DevOps exercises:")

if query:
    try:
        results = index.search(query, {"text": 1}, 3)

        if not results:
            st.warning("No results found.")
        else:
            for r in results:
                st.subheader(r.get("filename", "Unknown file"))
                st.caption(r.get("id", "No ID"))
                st.write((r.get("text", "")[:600]) + "...")
                st.markdown("---")

    except Exception as e:
        st.error(f"❌ Search error: {e}")

