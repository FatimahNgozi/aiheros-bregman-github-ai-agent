"""main.py — Streamlit app for DevOps Exercises Q&A using GitHub repo content."""

import streamlit as st
from dotenv import load_dotenv
import os
from application import ingest

# --- Load environment variables ---
load_dotenv()

# --- Default repo to use ---
REPO_OWNER = "bregman-arie"
REPO_NAME = "devops-exercises"

# --- Streamlit UI setup ---
st.set_page_config(page_title="DevOps Q&A Assistant", page_icon="🧠", layout="wide")
st.title("🧠 DevOps Exercises AI Assistant")
st.markdown("Ask me anything about **DevOps**, based on the open-source repo [bregman-arie/devops-exercises](https://github.com/bregman-arie/devops-exercises)")

# --- Cached function to avoid re-downloading GitHub data ---
@st.cache_resource(show_spinner="🔍 Indexing repository files...")
def load_index():
    """Load or build the searchable index from the GitHub repo."""
    try:
        index = ingest.index_data(REPO_OWNER, REPO_NAME)
        return index
    except Exception as e:
        st.error(f"Error building index: {e}")
        return None

# --- Initialize index ---
index = load_index()

if not index:
    st.stop()

# --- Simple search or question interface ---
query = st.text_input("💬 Ask a DevOps-related question or search for a topic:")
if query:
    with st.spinner("Searching..."):
        results = index.search(query, top_k=5)
        if not results:
            st.warning("No relevant information found.")
        else:
            st.subheader("📚 Top Results:")
            for r in results:
                st.markdown(f"**File:** `{r['filename']}`")
                st.markdown(f"[View on GitHub]({r['url']})")
                st.code(r['text'][:800] + "..." if len(r['text']) > 800 else r['text'])
                st.markdown("---")

