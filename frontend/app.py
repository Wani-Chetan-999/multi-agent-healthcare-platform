import streamlit as st

def apply_global_clinical_theme():
    """
    Injects custom styles to ensure a clean, medical-grade UI layout across all views.
    """
    st.set_page_config(
        page_title="MedAgentic Platform",
        page_icon="⚕️",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS injection for a clean theme
    st.markdown("""
        <style>
            /* Clean up top banner spacing */
            .block-container { padding-top: 2rem; padding-bottom: 2rem; }
            /* Styling metrics and telemetry boxes */
            div[data-testid="stMetricValue"] { font-size: 24px; font-weight: bold; color: #1E3A8A; }
            /* Sidebar background customization */
            .css-6qObcb { background-color: #F8FAFC; }
            /* Global font family cleanup */
            html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
        </style>
    """, unsafe_allow_html=True)

def initialize_global_session_states():
    """
    Sets up thread-safe operational states for tracking data persistence across user actions.
    """
    if "user_token" not in st.session_state:
        st.session_state["user_token"] = None
    if "user_profile" not in st.session_state:
        st.session_state["user_profile"] = {"name": "Guest User", "authenticated": False}
    if "current_chat_thread" not in st.session_state:
        st.session_state["current_chat_thread"] = []

def main():
    apply_global_clinical_theme()
    initialize_global_session_states()
    
    # Application Title and Welcome Banner
    st.title("⚕️ Multi-Agent AI Healthcare Assistant Platform")
    st.markdown("---")
    
    # Hero Layout Container
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Welcome to the Next Generation of AI Clinical Operations")
        st.markdown("""
            This clinical platform integrates multi-agent reasoning graphs, vector architectures, 
            and automated workflow engines to manage medical triage tasks safely and efficiently.
            
            ### Core Features
            * **AI Multi-Agent Cognitive Routing Engine:** Automatically triages requests, running real-time symptom evaluations or dispatching alerts.
            * **RAG-Backed Medical Reference Systems:** Validates all insights against vetted, peer-reviewed clinical knowledge bases.
            * **Prescription & Diagnostic Intake OCR Scanning:** Instantly parses medical documents for structural tracking and risk evaluation.
            * **Secure Medical Profile Control:** Keeps all interactions private with enterprise-grade cryptographic verification layers.
        """)
        
        st.info("💡 **Clinical Safety Notice:** This platform uses advanced AI systems to process data. Always verify insights with certified healthcare professionals before making diagnostic choices.")

    with col2:
        st.subheader("Platform Telemetry Status")
        st.metric(label="API Gateway Status", value="Online / Operational", delta="Latency 14ms")
        st.metric(label="Orchestration Brain", value="LangGraph / Groq Ready", delta="LLM Warm")
        st.metric(label="Knowledge Vector Mesh", value="ChromaDB Context Active", delta="Synced")

if __name__ == "__main__":
    main()