import streamlit as st
import asyncio

from application import ingest, search_agent, logs


# --- Initialization ---
@st.cache_resource
def init_agent():
    # 👇 Replace with your actual repo details
    repo_owner = "fatimah-adeniyi"
    repo_name = "aws-dms-migration"

    def filter(doc):
        # Filter optional: only index relevant files
        return doc["filename"].endswith(".py") or "dms" in doc["filename"].lower()

    st.write("🔄 Indexing your repository... please wait.")
    index = ingest.index_data(repo_owner, repo_name, filter=filter)
    agent = search_agent.init_agent(index, repo_owner, repo_name)
    return agent


# Load Gemini agent
agent = init_agent()


# --- Streamlit UI setup ---
st.set_page_config(page_title="AWS DMS Assistant", page_icon="🧠", layout="centered")
st.title("🧠 AWS DMS Assistant")
st.caption("Ask me anything about your AWS DMS migration repository.")


# --- Chat session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- Display past chat ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# --- Streaming helper ---
def stream_response(prompt: str):
    async def agen():
        async with agent.run_stream(user_prompt=prompt) as result:
            last_len = 0
            full_text = ""
            async for chunk in result.stream_output(debounce_by=0.02):
                new_text = chunk[last_len:]
                last_len = len(chunk)
                full_text = chunk
                if new_text:
                    yield new_text

            # 🪵 Log once finished
            logs.log_interaction_to_file(agent, result.new_messages())
            st.session_state._last_response = full_text

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    agen_obj = agen()

    try:
        while True:
            piece = loop.run_until_complete(agen_obj.__anext__())
            yield piece
    except StopAsyncIteration:
        return


# --- Handle new chat input ---
if prompt := st.chat_input("Ask your question about AWS DMS..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_text = st.write_stream(stream_response(prompt))

    final_text = getattr(st.session_state, "_last_response", response_text)
    st.session_state.messages.append({"role": "assistant", "content": final_text})
