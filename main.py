import streamlit as st
from application import ingest

# Configuration
REPO_OWNER = "bregman-arie"
REPO_NAME = "devops-exercises"

# ✅ Cache the index to avoid rebuilding every time
@st.cache_resource
def load_index():
    try:
        index = ingest.index_data(REPO_OWNER, REPO_NAME)
        return index
    except Exception as e:
        st.error(f"❌ Error building index: {e}")
        return None


# Streamlit UI setup
st.set_page_config(page_title="DevOps Exercises AI Agent", layout="wide")
st.title("🤖 DevOps Exercises AI Agent")
st.write("Ask any DevOps-related question based on the **DevOps Exercises** GitHub repository.")

# Load index
with st.spinner("🔍 Building or loading index..."):
    index = load_index()

if not index:
    st.stop()

# Query input
query = st.text_input("💬 Ask your question:")

if query:
    with st.spinner("🔎 Searching..."):
        try:
            results = index.search(query, ["text", "filename"], num_results=3)

            # ✅ Make sure 'results' is a list
            if isinstance(results, dict):
                results = list(results.values())
            elif not isinstance(results, list):
                st.warning("Unexpected result format from search()")
                st.write(results)
                st.stop()

            if not results:
                st.warning("No relevant documents found.")
            else:
                st.success(f"Found {len(results)} matching files!")

                for r in results:
                    if isinstance(r, dict):
                        st.markdown(f"### 📄 {r.get('filename', 'Unknown file')}")
                        st.caption(f"Path: `{r.get('id', '')}`")
                        snippet = r.get("text", "")[:600]
                        st.write(snippet + ("..." if len(snippet) >= 600 else ""))
                        st.markdown("---")
                    else:
                        st.warning(f"Unexpected result entry type: {type(r)}")

        except Exception as e:
            st.error(f"❌ Search error: {e}")
else:
    st.info("Type a question above to start searching through the DevOps Exercises content.")

