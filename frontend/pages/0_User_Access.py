import streamlit as st
from services.api_client import APIClient

st.set_page_config(page_title="Identity Vault", page_icon="🔒", layout="centered")

st.subheader("🔒 Patient Authentication portal")
st.markdown("---")

tab1, tab2 = st.tabs(["Login Active Session", "Register New Health Profile"])

with tab1:
    st.markdown("### Access Existing Records")
    login_email = st.text_input("Registered Email", key="login_em")
    login_password = st.text_input("Security Key / Password", type="password", key="login_pw")
    
    if st.button("Authenticate Identity", type="primary"):
        res = APIClient.login(login_email, login_password)
        if "access_token" in res:
            st.session_state["user_token"] = res["access_token"]
            st.session_state["user_profile"] = {"name": login_email, "authenticated": True}
            st.success(f"Identity confirmed. Welcome back, {login_email}!")
            st.balloons()
        else:
            st.error(f"Authentication Failed: {res.get('detail', 'Unknown error context.')}")

with tab2:
    st.markdown("### Initialize New Encrypted Patient Account")
    reg_name = st.text_input("Full Patient Name", key="reg_nm")
    reg_email = st.text_input("Active Clinical Email", key="reg_em")
    reg_password = st.text_input("Strong Security Key (8+ characters)", type="password", key="reg_pw")
    
    if st.button("Generate System Records"):
        if len(reg_password) < 8:
            st.warning("Password does not meet cryptographic length guidelines (8 characters min).")
        else:
            res = APIClient.register(reg_email, reg_password, reg_name)
            if "id" in res:
                st.success("Account initialized successfully! Please sign in using the login tab.")
            else:
                st.error(f"Registration Interrupted: {res.get('detail', 'Unknown failure conflict.')}")