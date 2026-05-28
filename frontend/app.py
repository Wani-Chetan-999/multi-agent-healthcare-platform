import streamlit as st
import httpx
import base64
import extra_streamlit_components as stx

# -------------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------------
st.set_page_config(
    page_title="AI Clinical Copilot",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)
# -------------------------------------------------------
# COOKIE SESSION PERSISTENCE
# -------------------------------------------------------
cookie_manager = stx.CookieManager()
saved_token = cookie_manager.get("copilot_jwt_token")

# -------------------------------------------------------
# HIGH-FIDELITY LUXURY CHAT INTERFACE OVERHAUL
# -------------------------------------------------------
st.markdown("""
<style>
/* Main configuration framework context */
.stApp {
    background-color: #081028;
    color: #F8FAFC;
}

/* Clear native element interference */
header { visibility: hidden; }

/* Constrain main thread layout to elegant readable reading limits */
.main .block-container {
    padding-top: 2rem;
    padding-bottom: 12rem; /* Reserves space so bottom text doesn't hide behind chat container */
    max-width: 840px;     
    margin: 0 auto;
}

/* Sidebar styling layout adjustments */
section[data-testid="stSidebar"] {
    background-color: #0B1220;
    border-right: 1px solid #1E293B;
}

section[data-testid="stSidebar"] .stButton button {
    width: 100%;
    border-radius: 12px;
    background: #2563EB;
    color: white;
    border: none;
    padding: 0.75rem;
    font-weight: 600;
}

section[data-testid="stSidebar"] .stButton button:hover {
    background: #1D4ED8;
}

/* Custom Message Dialog Bubbles Layout */
[data-testid="stChatMessage"] {
    border-radius: 20px;
    padding: 18px;
    margin-bottom: 1.25rem;
    max-width: 85%;
}

/* Assistant speech container position alignment */
[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-assistant"]) {
    background-color: #111827;
    border: 1px solid #1F2937;
    margin-right: auto;
}

/* User speech container position alignment */
[data-testid="stChatMessage"]:has(div[data-testid="chatAvatarIcon-user"]) {
    background-color: #1E293B;
    border: 1px solid #334155;
    margin-left: auto;
}

/* =========================================================
   🔥 CHATGPT / GEMINI STYLE FIXED INPUT + INLINE PLUS BUTTON
========================================================= */

/* Native Streamlit sticky bottom dock wrapper styling */
div[data-testid="stBottom"] {
    background: #081028 !important;
    border-top: 1px solid #1E293B !important;
    padding-top: 14px !important;
    padding-bottom: 24px !important;
    z-index: 9999 !important;
}

/* Center the chat layout columns width configuration */
div[data-testid="stBottom"] > div {
    max-width: 840px !important;
    margin: 0 auto !important;
}

/* Align columns inner structures vertically balanced */
div[data-testid="stBottom"] div[data-testid="stHorizontalBlock"] {
    align-items: center !important;
    gap: 8px !important;
}

/* Native chat input component container overrides */
div[data-testid="stChatInput"] {
    background: #111827 !important;
    border: 1px solid #1F2937 !important;
    border-radius: 28px !important;
    box-shadow:
        0 20px 25px -5px rgba(0,0,0,0.45),
        0 10px 10px -5px rgba(0,0,0,0.25);
    overflow: hidden !important;
    width: 100% !important;
}

/* Clear text area offsets inside the custom container view */
div[data-testid="stChatInput"] textarea {
    color: #F8FAFC !important;
    font-size: 15px !important;
    padding-left: 16px !important;
}

/* Send arrow positioning framework alignment */
div[data-testid="stChatInput"] button {
    right: 10px !important;
}

/* =========================================================
   INLINE + BUTTON POPOVER STYLING
========================================================= */

/* Make popover block container align clean and tight inside columns grid */
div[data-testid="element-container"]:has(div[data-testid="stPopover"]) {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
}

/* Reset baseline layout constraints on Popover blocks */
div[data-testid="stPopover"] {
    margin: 0 !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
}

div[data-testid="stPopover"] > div:first-child {
    margin: 0 !important;
    padding: 0 !important;
}

/* Circular Plus Action Icon configuration rules */
div[data-testid="stPopover"] button {
    width: 44px !important;
    height: 44px !important;
    min-width: 44px !important;
    border-radius: 50% !important;
    border: 1px solid #1F2937 !important;
    background: #111827 !important;
    color: #94A3B8 !important;
    font-size: 24px !important;
    padding: 0 !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
}

/* Hover interactive dynamic transition feedback scaling */
div[data-testid="stPopover"] button:hover {
    color: #FFFFFF !important;
    border-color: #3B82F6 !important;
    background: #1E293B !important;
    transform: scale(1.06);
}

/* Clear out original downward native dropdown indicator arrow */
div[data-testid="stPopover"] svg {
    display: none !important;
}

/* Formatting adjustments for the staging file indicators directly above the input block */
.staged-file-container {
    margin-bottom: 12px;
    display: flex;
    justify-content: flex-start;
    padding: 0 12px;
}

.preview-card {
    background: #1E293B;
    border: 1px solid #334155;
    padding: 8px 14px;
    border-radius: 12px;
    display: inline-flex;
    align-items: center;
    gap: 10px;
    font-size: 13px;
}

/* Minimalist File uploader hide text rules */
[data-testid="stFileUploaderDropzoneInstructions"] { display: none; }
[data-testid="stFileUploaderDropzone"] { border: none; background: transparent; padding: 0; }

/* Welcome Presentation UI layout */
.welcome-title {
    text-align: center;
    font-size: 42px;
    font-weight: 700;
    margin-top: 40px;
    background: linear-gradient(45deg, #3B82F6, #60A5FA);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.welcome-subtitle {
    text-align: center;
    color: #94A3B8;
    font-size: 16px;
    margin-top: 8px;
}

.capability-card {
    background: #111827;
    border: 1px solid #1F2937;
    padding: 24px;
    border-radius: 16px;
    margin-top: 20px;
    height: 100%;
}

.capability-title {
    font-size: 16px;
    font-weight: 600;
    color: #F8FAFC;
    margin-bottom: 6px;
}

.capability-desc {
    color: #9CA3AF;
    font-size: 13px;
    line-height: 1.4;
}

/* Target ONLY the secondary button components globally */
button[kind="secondary"][data-testid="baseButton-secondary"] {
    background: #2563EB;
}

/* =========================================================
   🚨 ABSOLUTE OVERRIDE BYPASS FOR LOGOUT BUTTON
========================================================= */
/* Targets the layout element that contains the exact button string text fallback */
div[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div.element-container:last-child button,
div[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] .stButton button:has(div:contains("🚪")),
div[data-testid="stSidebar"] button:has(div:contains("Log Out")) {
    background-color: #7F1D1D !important;
    color: #FFFFFF !important;
    border: 1px solid #B91C1C !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
}

/* Forced hover handling states */
div[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] div.element-container:last-child button:hover,
div[data-testid="stSidebar"] div[data-testid="stVerticalBlock"] .stButton button:has(div:contains("🚪")):hover,
div[data-testid="stSidebar"] button:has(div:contains("Log Out")):hover {
    background-color: #991B1B !important;
    border-color: #EF4444 !important;
    color: #FFFFFF !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------
# SESSION STATE INITIALIZATION
# -------------------------------------------------------
if "user_token" not in st.session_state:
    st.session_state["user_token"] = None

# Restore token ONLY if available
if saved_token and not st.session_state["user_token"]:
    st.session_state["user_token"] = saved_token

if "active_thread_id" not in st.session_state:
    st.session_state["active_thread_id"] = None

if "ui_messages" not in st.session_state:
    st.session_state["ui_messages"] = []

if "staged_file" not in st.session_state:
    st.session_state["staged_file"] = None

if "uploader_reset_counter" not in st.session_state:
    st.session_state["uploader_reset_counter"] = 0

# -------------------------------------------------------
# AUTHENTICATION GUARD (LOGIN / REGISTER)
# -------------------------------------------------------
if not st.session_state["user_token"]:
    st.markdown('<div class="welcome-title">🩺 AI Clinical Copilot</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-subtitle">Unified Healthcare Intelligence Workspace</div>', unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        login_col, register_col = st.columns(2)

        with login_col:
            if st.button("Log In", use_container_width=True):
                try:
                    response = httpx.post(
                        "http://localhost:8000/api/v1/auth/login",
                        data={"username": email, "password": password}
                    )
                    if response.status_code == 200:
                        token = response.json()["access_token"]
                        st.session_state["user_token"] = token
                        cookie_manager.set(
                            "copilot_jwt_token",
                            token,
                            expires_at=None
                        )
                        st.rerun()
                    else:
                        st.error("Invalid credentials.")
                except Exception as e:
                    st.error(str(e))

        with register_col:
            if st.button("Register", use_container_width=True):
                try:
                    response = httpx.post(
                        "http://localhost:8000/api/v1/auth/register",
                        json={"email": email, "password": password, "full_name": "Healthcare User"}
                    )
                    if response.status_code == 201:
                        st.success("Account created successfully.")
                    else:
                        st.error(response.text)
                except Exception as e:
                    st.error(str(e))
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state['user_token']}"}

# -------------------------------------------------------
# LOAD CONVERSATION HISTORY
# -------------------------------------------------------
def load_conversation_history(thread_id: str):
    try:
        response = httpx.get(
            f"http://localhost:8000/api/v1/copilot/threads/{thread_id}/messages",
            headers=headers
        )
        if response.status_code == 200:
            st.session_state["ui_messages"] = response.json()
        else:
            st.session_state["ui_messages"] = []
    except Exception as e:
        st.error(f"History sync failed: {str(e)}")

# -------------------------------------------------------
# SIDEBAR NAVIGATION
# -------------------------------------------------------
with st.sidebar:
    st.markdown("## 🩺 Clinical Copilot")
    
    if st.button("➕ New Consultation"):
        try:
            response = httpx.post("http://localhost:8000/api/v1/copilot/threads", headers=headers)
            if response.status_code == 201:
                st.session_state["active_thread_id"] = response.json()["conversation_id"]
                st.session_state["ui_messages"] = []
                st.session_state["staged_file"] = None
                st.rerun()
        except Exception as e:
            st.error(str(e))

    st.markdown("---")
    st.markdown("### 🕒 Recent Consultations")

    try:
        response = httpx.get("http://localhost:8000/api/v1/copilot/threads", headers=headers)
        if response.status_code == 200:
            for thread in response.json():
                title = thread.get("title", "Untitled Consultation")
                if st.button(f"💬 {title}", key=thread["conversation_id"]):
                    st.session_state["active_thread_id"] = thread["conversation_id"]
                    st.session_state["staged_file"] = None
                    load_conversation_history(thread["conversation_id"])
                    st.rerun()
    except:
        st.caption("Unable to load consultations")

    st.markdown("---")

    if st.button("🚪 Log Out", key="logout_button"):
        cookie_manager.delete("copilot_jwt_token")
        st.session_state["user_token"] = None
        st.session_state["active_thread_id"] = None
        st.session_state["ui_messages"] = []
        st.rerun()
        

# -------------------------------------------------------
# LANDING SCREEN (NO ACTIVE THREAD)
# -------------------------------------------------------
if not st.session_state["active_thread_id"]:
    st.markdown('<div class="welcome-title">🩺 AI Clinical Copilot</div>', unsafe_allow_html=True)
    st.markdown('<div class="welcome-subtitle">Your unified healthcare assistant for intelligent medical conversations</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="capability-card"><div class="capability-title">🤒 Symptom Analysis</div><div class="capability-desc">Analyze patient symptoms and triage critical medical conditions seamlessly.</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="capability-card"><div class="capability-title">📄 Report Understanding</div><div class="capability-desc">Upload clinical prescriptions, diagnostic charts, or lab reports for quick processing.</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="capability-card"><div class="capability-title">🎙️ Voice Consultation</div><div class="capability-desc">Transcribe and analyze verbal patient workflows using conversational AI models.</div></div>', unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.info("👈 Choose an existing consultation or start a new one from the sidebar to begin.")
    st.stop()

# -------------------------------------------------------
# CHAT RENDER LOOP
# -------------------------------------------------------
thread_id = st.session_state["active_thread_id"]

for message in st.session_state["ui_messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# =======================================================
# 📌 SEAMLESS EMBEDDED CONSOLE DOCK ENTRYBAR
# =======================================================
# File indicator rendering step above the input track
if st.session_state["staged_file"]:
    f_name = st.session_state["staged_file"]["name"]
    f_type = st.session_state["staged_file"]["type"]
    icon = "🎙️" if "audio" in f_type or f_name.endswith(('mp3','wav','m4a')) else "📄"
    
    st.markdown('<div class="staged-file-container">', unsafe_allow_html=True)
    preview_col1, preview_col2 = st.columns([6, 1])
    with preview_col1:
        st.markdown(f'<div class="preview-card"><span>{icon}</span><b>{f_name}</b></div>', unsafe_allow_html=True)
    with preview_col2:
        if st.button("❌ Clear", key="clear_attachment", help="Remove file context"):
            st.session_state["staged_file"] = None
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# Structurally bound entrybar layout
with st.container():
    input_col1, input_col2 = st.columns([1, 16])

    with input_col1:
        with st.popover("＋", help="Upload context records"):
            st.markdown("### Context Attachments")
            
            raw_doc = st.file_uploader(
                "Upload Documentation / Images",
                type=["png", "jpg", "jpeg", "pdf"],
                key=f"doc_uploader_widget_{st.session_state['uploader_reset_counter']}"
            )
            
            raw_voice = st.file_uploader(
                "Upload Voice Consult Record",
                type=["wav", "mp3", "m4a"],
                key=f"voice_uploader_widget_{st.session_state['uploader_reset_counter']}"
            )
            
            if raw_doc:
                st.session_state["staged_file"] = {
                    "name": raw_doc.name,
                    "type": raw_doc.type,
                    "bytes": raw_doc.read()
                }
                
                
            elif raw_voice:
                st.session_state["staged_file"] = {
                    "name": raw_voice.name,
                    "type": raw_voice.type,
                    "bytes": raw_voice.read()
                }
                

    with input_col2:
        user_text = st.chat_input("Ask about symptoms, reports, medications, or historical patterns...")


# -------------------------------------------------------
# DATA DISPATCH PIPELINE EXECUTION
# -------------------------------------------------------
if user_text:
    attached_file = st.session_state.get("staged_file")

    if attached_file:
        file_name = attached_file["name"]
        file_type = attached_file["type"]
        icon = "🎙️" if ("audio" in file_type or file_name.endswith(("mp3", "wav", "m4a"))) else "📄"

        user_display = f"{icon} **Attached File:** `{file_name}`\n\n{user_text}"
    else:
        user_display = user_text

    # Store user submission
    st.session_state["ui_messages"].append({
        "role": "user",
        "content": user_display
    })

    # Render immediate screen response state
    with st.chat_message("user"):
        st.markdown(user_display)

    # Initialize submission transaction package parameters
    payload = {
        "conversation_id": thread_id,
        "message": user_text,
        "attached_file_b64": None,
        "attached_file_name": None,
        "attached_file_mime": None
    }

    if attached_file:
        payload["attached_file_b64"] = base64.b64encode(attached_file["bytes"]).decode("utf-8")
        payload["attached_file_name"] = attached_file["name"]
        payload["attached_file_mime"] = attached_file["type"]

    # Request network connection exchange session block
    with st.chat_message("assistant"):
        with st.spinner("Clinical reasoning engine active..."):
            try:
                response = httpx.post(
                    "http://localhost:8000/api/v1/copilot/copilot-execute",
                    json=payload,
                    headers=headers,
                    timeout=180
                )

                if response.status_code == 200:
                    response_json = response.json()
                    assistant_response = response_json.get("response_text", "No response returned from backend.")
                    st.markdown(assistant_response)

                    st.session_state["ui_messages"].append({
                        "role": "assistant",
                        "content": assistant_response
                    })
                else:
                    error_text = f"❌ **Backend Processing Error**\n\nStatus Code: {response.status_code}\n\n`{response.text}`"
                    st.error(error_text)
                    st.session_state["ui_messages"].append({
                        "role": "assistant",
                        "content": error_text
                    })

            except Exception as e:
                error_text = f"🚨 **Connection Failure**\n\n{str(e)}"
                st.error(error_text)
                st.session_state["ui_messages"].append({
                    "role": "assistant",
                    "content": error_text
                })

    # Clear staged items and trigger a clean refresh
    st.session_state["staged_file"] = None
    # Force uploader recreation
    st.session_state["uploader_reset_counter"] += 1
    st.rerun()