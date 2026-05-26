import streamlit as st
import httpx

st.set_page_config(page_title="Knowledge Ingestion", page_icon="📚", layout="wide")
st.subheader("📚 Clinical Knowledge Base Ingestion Workspace")
st.markdown("---")

if not st.session_state.get("user_token"):
    st.warning("⚠️ Access Denied. Please authenticate via the User Access portal to log into the database ingestion systems.")
    st.stop()

st.markdown("### Index New Reference Documentation")
doc_title = st.text_input("Document/Manual Reference Title", placeholder="Example: WHO-Hypertension-Protocol-2026")
doc_text = st.text_area("Raw Reference Manual Content Body (Text Context Only)", placeholder="Paste full textbook data chapters here...", height=250)

if st.button("Generate Embedding Vectors & Index Document", type="primary"):
    if not doc_title or not doc_text:
        st.warning("Both the reference title and text content parameters are required for ingestion.")
    else:
        headers = {"Authorization": f"Bearer {st.session_state['user_token']}"}
        payload = {"document_title": doc_title, "raw_text_content": doc_text}
        
        with st.spinner("Executing chunk processing operations and vector calculations..."):
            try:
                res = httpx.post("http://localhost:8000/api/v1/medical/ingest-knowledge", json=payload, headers=headers, timeout=60.0)
                if res.status_code == 201:
                    st.success(f"Success! '{doc_title}' has been successfully indexed into the ChromaDB vector database grid.")
                    st.balloons()
                else:
                    st.error(f"Ingestion process interrupted. Server response code: {res.status_code}")
            except Exception as e:
                st.error(f"Network processing exception encountered: {str(e)}")