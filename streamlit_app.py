import streamlit as st
import requests

BACKEND_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Chat with your links", layout="wide")

if "urls" not in st.session_state:
    st.session_state.urls = []
if "messages" not in st.session_state:
    st.session_state.messages = []
if "urls_processed" not in st.session_state:
    st.session_state.urls_processed = False

left, right = st.columns([1, 2])

with left:
    st.header("Links")

    with st.form("add_url_form", clear_on_submit=True):
        new_url = st.text_input("Add a URL", placeholder="https://example.com/article")
        submitted = st.form_submit_button("Add")
        if submitted and new_url.strip():
            if new_url.strip() not in st.session_state.urls:
                st.session_state.urls.append(new_url.strip())
                st.session_state.urls_processed = False
            else:
                st.warning("This URL is already added.")

    st.divider()

    if not st.session_state.urls:
        st.caption("No URLs added yet.")
    else:
        for i, url in enumerate(st.session_state.urls):
            c1, c2 = st.columns([5, 1])
            c1.write(url)
            if c2.button("Delete", key=f"del_{i}"):
                st.session_state.urls.pop(i)
                st.session_state.urls_processed = False
                st.rerun()

    st.divider()

    process_disabled = len(st.session_state.urls) == 0
    if st.button("Process URLs", disabled=process_disabled, use_container_width=True):
        with st.spinner("Processing..."):
            try:
                resp = requests.post(
                    f"{BACKEND_URL}/rag/ingest-urls",
                    json={"urls": st.session_state.urls},
                    timeout=120,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    st.success(f"Done. Chunks created: {data.get('chunks_created', '?')}")
                    st.session_state.urls_processed = True
                else:
                    st.error(f"Error ({resp.status_code}): {resp.text}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend at " + BACKEND_URL)
            except requests.exceptions.Timeout:
                st.error("Request timed out.")

    if st.session_state.urls_processed:
        st.info("URLs are ready. Ask about them on the right.")

with right:
    st.header("Chat")

    chat_container = st.container(height=500)
    with chat_container:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if msg.get("sources"):
                    with st.expander("Sources"):
                        for s in msg["sources"]:
                            st.caption(s)

    question = st.chat_input("Type your question...")
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with chat_container:
            with st.chat_message("user"):
                st.markdown(question)

            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        resp = requests.post(
                            f"{BACKEND_URL}/chatbot/chat",
                            json={"question": question},
                            timeout=60,
                        )
                        if resp.status_code == 200:
                            data = resp.json()
                            answer = data.get("answer", "")
                            sources = data.get("sources", [])
                            st.markdown(answer)
                            if sources:
                                with st.expander("Sources"):
                                    for s in sources:
                                        st.caption(s)
                            st.session_state.messages.append(
                                {"role": "assistant", "content": answer, "sources": sources}
                            )
                        else:
                            err = f"Error ({resp.status_code}): {resp.text}"
                            st.error(err)
                            st.session_state.messages.append({"role": "assistant", "content": err})
                    except requests.exceptions.ConnectionError:
                        err = "Could not connect to the backend at " + BACKEND_URL
                        st.error(err)
                        st.session_state.messages.append({"role": "assistant", "content": err})