import streamlit as st
from application import ingest
from dotenv import load_dotenv
import os

# Load environment variables (includes GITHUB_TOKEN)
load_dotenv()

# Set repo info (you can edit this if needed)
REPO_OWNER = "bregman-arie"
REPO_NAME = "devops-exercises"

# --------------------------------------------------------------------
# Streamlit app configuration
# --------------------------------------------------------------------
st.set_page_config(page_title="AIHEROS – Bregman GitHub AI Agent", layout="wide")

st.title("🤖 AIHEROS – Bregman GitHub AI Agent")
st.write("Search and explore DevOps exercises directly from [bregman-arie/devops-exercises](https://github.com/bregman-arie/devops-exercises).")

# --------------------------------------------------------------------
# Cache index building to avoid rebuilding every time
# --------------------------------------------------------------------
@st.cache_resource(show_spinner=True)
def build_index():
    try:
        index = ingest.index_data(REPO_OWNER, REPO_NAME)
        return index
    except Exception as e:
        st.error(f"❌ Error building index: {e}")
        return None


# --------------------------------------------------------------------
# Build index once
# --------------------------------------------------------------------
with st.spinner("📦 Building index from GitHub repo..."):
    index = build_index()

if index is not None:
    st.success("✅ Index built successfully!")
else:
    st.stop()

# --------------------------------------------------------------------
# Search interface
# --------------------------------------------------------------------
query = st.text_input("🔍 Enter your search query:")
if query:
    try:
        results = index.search(query, num_results=10)
        if results:
            st.write(f"### 🧾 Top {len(results)} results for: `{query}`")
            for r in results:
                st.markdown(f"**📄 File:** `{r['filename']}`")
                st.markdown(f"**🗂 Path:** `{r['id']}`")
                st.write(r['text'][:500] + "...")
                st.divider()
        else:
            st.warning("No results found.")
    except Exception as e:
        st.error(f"❌ Search error: {e}")

