import streamlit as st
from application import ingest

# 🔧 Configuration
REPO_OWNER = "bregman-arie"
REPO_NAME = "devops-exercises"

# ✅ Cache the index to avoid rebuilding on every reload
@st.cache_resource
def load_index():
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
st.sidebar.info("Refreshing rebuilds the index from GitHub and updates the local cache.")

# ✅ Load the search index
with st.spinner("🔍 Building or loading index..."):
    index = load_index()

if not index:
    st.stop()

# ✅ Search input
query = st.text_input("💬 Ask your question:")

if query:
    with st.spinner("🔎 Searching..."):
        try:
            results = index.search(query, ["text"], num_results=3)

            # Handle results that might be nested lists
            if isinstance(results, list):
                # Flatten in case minsearch returns [[...], [...]]
                flattened = []
                for r in results:
                    if isinstance(r, list):
                        flattened.extend(r)
                    else:
                        flattened.append(r)
                results = flattened

            # Validate structure
            if not results or not isinstance(results[0], dict):
                st.error("⚠️ Unexpected search result format — expected a list of dicts.")
                st.write("🔍 Raw results:", results)
                st.stop()

            # ✅ Display results
            st.success(f"Found {len(results)} matching files!")
            for r in results:
                filename = r.get("filename", "Unknown file")
                path = r.get("id", "")
                text = r.get("text", "")[:600]

                st.markdown(f"### 📄 {filename}")
                st.caption(f"Path: `{path}`")
                st.write(text + ("..." if len(text) == 600 else ""))
                st.markdown("---")

        except Exception as e:
            st.error(f"❌ Search error: {e}")
else:
    st.info("Type a question above to start searching through the DevOps Exercises content.")

