import streamlit as st
from dotenv import load_dotenv
import os
from application import ingest
import time

# ----------------------------------------------------------------------
# Load environment variables
# ----------------------------------------------------------------------
load_dotenv()
repo_owner = "bregman-arie"
repo_name = "devops-exercises"
token = os.getenv("GITHUB_TOKEN")

# ----------------------------------------------------------------------
# Streamlit Page Setup
# ----------------------------------------------------------------------
st.set_page_config(page_title="DevOps Exercises Search", layout="wide")
st.title("🧠 DevOps Exercises Search Assistant")
st.caption(f"Indexing GitHub repo: **{repo_owner}/{repo_name}**")

# ----------------------------------------------------------------------
# Build index (cached)
# ----------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_index():
    with st.spinner("Building searchable index from GitHub..."):
        try:
            index = ingest.index_data(repo_owner, repo_name)
            return index
        except Exception as e:
            st.error(f"❌ Error building index: {e}")
            return None

index = load_index()

if not index:
    st.stop()

st.success("✅ Index built successfully! You can now search below.")

# ----------------------------------------------------------------------
# Search Interface
# ----------------------------------------------------------------------
query = st.text_input("🔍 Enter your DevOps question or topic:", "")

if query:
    st.write("Searching...")
    start = time.time()
    results = index.search(query, top_k=10)
    elapsed = time.time() - start

    if results:
        st.success(f"✅ Found {len(results)} results in {elapsed:.2f}s.")
        for r in results:
            with st.expander(r["filename"]):
                st.markdown(f"**File:** `{r['id']}`")
                st.markdown("---")
                st.markdown(r["text"][:1000] + "...")
    else:
        st.warning("⚠️ No results found.")
else:
    st.info("👆 Type a query above to start searching.")

