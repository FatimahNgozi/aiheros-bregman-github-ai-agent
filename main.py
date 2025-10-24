
import streamlit as st
from application import ingest

# 🔧 Configuration
REPO_OWNER = "bregman-arie"
REPO_NAME = "devops-exercises"


# ✅ Cache the index to avoid rebuilding on every reload
@st.cache_resource
def load_index(force_refresh=False):
    try:
        index = ingest.index_data(REPO_OWNER, REPO_NAME)
        return index
    except Exception as e:
        st.error(f"❌ Error building index: {e}")
        return None


# ✅ App title
st.set_page_config(page_title="Bregman DevOps AI Agent", layout="wide")
st.title("🤖 Bregman DevOps Exercises AI Agent")
st.write("Ask any DevOps-related question based on the **DevOps Exercises** GitHub repository.")

# ✅ Sidebar controls
st.sidebar.header("⚙️ Controls")
refresh = st.sidebar.button("🔄 Refresh Index (Force Rebuild)")
st.sidebar.info("Refreshing rebuilds the index from GitHub and updates the local cache.")

# ✅ Load the search index
with st.spinner("🔍 Building or loading index..."):
    index = load_index(force_refresh=refresh)

if not index:
    st.stop()

# ✅ Search input
query = st.text_input("💬 Ask your question:")

if query:
    with st.spinner("🔎 Searching..."):
        try:
            results = index.search(query, ["text"], num_results=3)

            if not results:
                st.warning("No relevant documents found.")
            else:
                st.success(f"Found {len(results)} matching files!")
                for r in results:  # ✅ results is a list of dicts
                    st.markdown(f"### 📄 {r.get('filename', 'Unknown file')}")
                    st.caption(f"Path: `{r.get('id', '')}`")
                    snippet = r.get('text', '')[:600]
                    st.write(snippet + ("..." if len(snippet) == 600 else ""))
                    st.markdown("---")

        except Exception as e:
            st.error(f"❌ Search error: {e}")

else:
    st.info("Type a question above to start searching through the DevOps Exercises content.")
