import streamlit as st
import httpx

st.set_page_config(page_title="Document Intake", page_icon="📋", layout="wide")
st.subheader("📋 Intelligent Medical Document Intake Workstation")
st.markdown("---")

if not st.session_state.get("user_token"):
    st.warning("⚠️ Access Denied. Please authenticate via the User Access portal to log into the document intake system.")
    st.stop()

doc_type = st.radio("Select Target Document Category for Intake Parsing:", ["Prescription Scanner", "Diagnostic Lab Report Analyzer"], horizontal=True)

uploaded_file = st.file_uploader("Upload a clear digital image snapshot (.png, .jpg, .jpeg)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Render an immediate preview layout of the uploaded image
    st.image(uploaded_file, caption="Uploaded Intake Document Preview Source", width=350)
    
    if st.button("Execute Document Processing Execution Pipeline", type="primary"):
        headers = {"Authorization": f"Bearer {st.session_state['user_token']}"}
        
        # Prepare the binary multi-part form payload structure
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        
        with st.spinner("Executing OCR scanning and agent extraction structures..."):
            try:
                if doc_type == "Prescription Scanner":
                    res = httpx.post("http://localhost:8000/api/v1/medical/scan-prescription", files=files, headers=headers, timeout=60.0)
                    
                    if res.status_code == 200:
                        data = res.json()
                        st.success("Prescription Parsing Sequence Concluded.")
                        st.markdown(f"**Identified Patient Record:** {data.get('patient_name') or 'Not Specified'}")
                        
                        st.markdown("#### Extracted Medications List Matrix")
                        if data.get("medications"):
                            st.table(data["medications"])
                        else:
                            st.caption("No individual active medications resolved.")
                            
                        if data.get("clinical_warnings"):
                            st.markdown("#### Clinical Safety Review Flags")
                            for warn in data["clinical_warnings"]:
                                st.warning(warn)
                    else:
                        st.error(f"Processing error encountered. Status Code: {res.status_code}")
                        
                else:  # Diagnostic Lab Report Analyzer
                    res = httpx.post("http://localhost:8000/api/v1/medical/analyze-report", files=files, headers=headers, timeout=60.0)
                    
                    if res.status_code == 200:
                        data = res.json()
                        st.success("Diagnostic Report Parsing Sequence Concluded.")
                        st.markdown(f"### Panel Title: {data['panel_title']}")
                        
                        st.markdown("#### Extracted Biomarker Analytics")
                        if data.get("biomarkers"):
                            st.table(data["biomarkers"])
                        else:
                            st.caption("No matching clinical biomarkers extracted.")
                            
                        st.markdown("#### Educational Context Summary")
                        st.info(data["summary_analysis"])
                    else:
                        st.error(f"Processing error encountered. Status Code: {res.status_code}")
                        
            except Exception as e:
                st.error(f"Transport layer network processing crash: {str(e)}")