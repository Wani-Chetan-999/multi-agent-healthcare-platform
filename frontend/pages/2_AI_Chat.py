import streamlit as st
import httpx
import uuid

st.set_page_config(page_title="Agentic Workspace", page_icon="💬", layout="wide")
st.subheader("🤖 LangGraph Orchestrated Clinical Workspace")
st.markdown("---")

if not st.session_state.get("user_token"):
    st.warning("⚠️ Access Denied. Log in via the User Access portal to activate this agent workstation.")
    st.stop()

if "session_tracking_id" not in st.session_state:
    st.session_state["session_tracking_id"] = str(uuid.uuid4())
if "ui_chat_history" not in st.session_state:
    st.session_state["ui_chat_history"] = []

for msg in st.session_state["ui_chat_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Ask a general clinical system question or log current physical symptoms..."):
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state["ui_chat_history"].append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("LangGraph router evaluation active..."):
            headers = {"Authorization": f"Bearer {st.session_state['user_token']}"}
            payload = {
                "session_id": st.session_state["session_tracking_id"],
                "message": user_input
            }
            
            try:
                # Issue unified request to the multi-agent cognitive engine
                response = httpx.post(
                    "http://localhost:8000/api/v1/agentic/agentic-execute", 
                    json=payload, 
                    headers=headers,
                    timeout=45.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    ai_reply = data["response"]
                    path_used = data["dispatched_path"]
                    
                    # Display the execution route taken by the graph
                    st.caption(f"⚡ Cognitive Route Dispatched: `{path_used}`")
                    st.markdown(ai_reply)
                    st.session_state["ui_chat_history"].append({"role": "assistant", "content": ai_reply})
                else:
                    st.error(f"Orchestration failure error code: {response.status_code}")
            except Exception as e:
                st.error(f"Network transport failure: {str(e)}")