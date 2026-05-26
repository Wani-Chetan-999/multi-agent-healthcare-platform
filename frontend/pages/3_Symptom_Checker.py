import streamlit as st
import httpx

st.set_page_config(page_title="Triage Diagnostics", page_icon="🩺", layout="wide")

st.subheader("🩺 Clinical Symptom Assessment Workstation")
st.markdown("---")

if not st.session_state.get("user_token"):
    st.warning("⚠️ Access Denied. Please navigate to the User Access portal and log in to use the Symptom Workstation.")
    st.stop()

st.markdown("### Enter Current Observable Symptoms")
st.write("Provide a detailed description of your symptoms, including how long you've experienced them, their severity, and any specific areas of discomfort.")

symptom_input = st.text_area(
    "Symptom Log Input Field", 
    placeholder="Example: I've had severe, crushing chest pain for the last 15 minutes that spreads to my left arm, and I am feeling very dizzy...",
    height=150,
    label_visibility="collapsed"
)

if st.button("Run Clinical Triage Assessment", type="primary"):
    if not symptom_input.strip():
        st.warning("Please describe your symptoms before running the assessment engine.")
    else:
        headers = {"Authorization": f"Bearer {st.session_state['user_token']}"}
        payload = {"symptoms_text": symptom_input}
        
        with st.spinner("Analyzing symptom metrics across risk databases..."):
            try:
                response = httpx.post(
                    "http://localhost:8000/api/v1/medical/triage-check",
                    json=payload,
                    headers=headers,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 1. Evaluate emergency status and show high-visibility alerts if needed
                    if data["is_emergency"]:
                        st.error("🚨 CRITICAL HEALTH RISK DETECTED — EMERGENCY PROTOCOL ACTIVATED")
                        st.markdown(f"""
                            <div style="background-color:#FEE2E2; border-left:8px solid #DC2626; padding:20px; border-radius:4px; margin-bottom:20px;">
                                <h4 style="color:#991B1B; margin-top:0;">⚠️ IMMEDIATE ACTION REQUIRED</h4>
                                <p style="color:#7F1D1D; font-weight:500; font-size:16px;">
                                    The system has flagged these symptoms as potentially life-threatening. 
                                    Please call emergency services (like 911 or your local emergency number) 
                                    or go to the nearest emergency room immediately.
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.success("✅ Assessment Concluded: No immediate life-threatening emergency indicators found.")
                    
                    # 2. Display metadata telemetry cards
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Assigned Severity Tier", data["severity_tier"])
                    with col2:
                        st.write("**Extracted Risk Risk Factors:**")
                        if data["risk_factors"]:
                            for factor in data["risk_factors"]:
                                st.markdown(f"* {factor}")
                        else:
                            st.caption("No high-risk emergency markers detected.")
                    
                    st.markdown("---")
                    
                    # 3. Render educational guidance sections
                    st.markdown("### Clinical Educational Summary")
                    st.info(data["clinical_educational_guidance"])
                    
                    st.markdown("### System Compliance Notice")
                    st.caption(data["safety_disclaimer"])
                    
                else:
                    st.error(f"Analysis interrupted by server error code: {response.status_code}")
                    
            except Exception as e:
                st.error(f"Network transport layer crash: {str(e)}")