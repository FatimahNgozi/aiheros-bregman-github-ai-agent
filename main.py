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
    with st.spinner("Searching..."):
        try:
            results = index.search(query, ["text"], num_results=5)
            if not results:
                st.warning("No results found — try other keywords.")
            else:
                st.success(f"Found {len(results)} results")
                for r in results:
                    st.markdown(f"### 📄 {r.get('filename', r.get('id'))}")
                    st.caption(r.get('id'))
                    st.write(r.get('text', '')[:1000] + "...")
                    st.markdown("---")
        except Exception as e:
            st.error(f"❌ Search error: {e}")
________________________________________
pyproject.toml (recommended)
Notes: the original project had a requires-python constraint that didn’t match Streamlit’s environment and caused cohere/pydantic-ai resolution problems. This pyproject.toml tightens the python range to <4.0 and removes pydantic-ai which pulls cohere.
[project]
name = "devops-ai-agent"
version = "0.1.0"
description = "DevOps Exercises AI Agent — optimized"
readme = "README.md"
requires-python = ">=3.10,<4.0"

dependencies = [
  "streamlit>=1.36.0",
  "openai>=1.11.0",
  "minsearch>=0.0.7", # explicit newer version
  "python-frontmatter>=1.1.0",
  "requests>=2.32.3",
  "sentence-transformers>=3.0.1",
  "tqdm>=4.66.4",
  "python-dotenv>=1.0.0",
]

[tool.uv.workspace]
members = ["application", "application/application"]

