import streamlit as st
import httpx
import uuid

st.set_page_config(page_title="Clinical AI Workspace", page_icon="💬", layout="wide")

st.subheader("💬 Clinical AI Consultation Workspace")
st.markdown("---")

# Verify user session authentication status before rendering interface elements
if not st.session_state.get("user_token"):
    st.warning("⚠️ Access Denied. Please navigate to the User Access portal and log in to view this workstation.")
    st.stop()

# Initialize an independent session ID for separate tracking contexts
if "session_tracking_id" not in st.session_state:
    st.session_state["session_tracking_id"] = str(uuid.uuid4())

# Local session storage for immediate UI layout updates
if "ui_chat_history" not in st.session_state:
    st.session_state["ui_chat_history"] = []

# Display previous messages in the current UI session
for msg in st.session_state["ui_chat_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Handle new user inputs
if user_input := st.chat_input("Enter your medical system query or symptoms analysis request here..."):
    # Render user query instantly
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state["ui_chat_history"].append({"role": "user", "content": user_input})

    # Render assistant placeholder to receive streaming chunks
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        accumulated_response = ""
        
        headers = {"Authorization": f"Bearer {st.session_state['user_token']}"}
        payload = {
            "session_id": st.session_state["session_tracking_id"],
            "message": user_input
        }
        
        try:
            # Open a streaming context connection to the backend server
            with httpx.stream(
                "POST", 
                "http://localhost:8000/api/v1/chat/stream", 
                json=payload, 
                headers=headers,
                timeout=60.0
            ) as response:
                if response.status_code != 200:
                    st.error(f"Server integration failure. Code: {response.status_code}")
                else:
                    for chunk in response.iter_text():
                        accumulated_response += chunk
                        # Update the UI live as tokens arrive
                        response_placeholder.markdown(accumulated_response + "▌")
                    
                    # Final clean render without the typing indicator cursor
                    response_placeholder.markdown(accumulated_response)
                    st.session_state["ui_chat_history"].append({"role": "assistant", "content": accumulated_response})
                    
        except Exception as e:
            st.error(f"Transport layer network crash: {str(e)}")