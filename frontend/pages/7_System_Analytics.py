import streamlit as st
import httpx
import time

st.set_page_config(page_title="System Analytics", page_icon="📊", layout="wide")
st.subheader("📊 Live Platform Telemetry & Performance Dashboard")
st.markdown("---")

if not st.session_state.get("user_token"):
    st.warning("⚠️ Access Denied. Please authenticate via the User Access portal to log into the telemetry systems.")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state['user_token']}"}

st.markdown("### Execution Ping Optimizer")
st.write("Click below to run a diagnostic health-check request across our network layers and measure your active connection latency:")

if st.button("Execute Active Ping Diagnostic", type="primary"):
    payload = {"session_id": "diagnostic", "message": "Ping check"}
    
    try:
        # Capture raw execution durations on the client side
        client_start = time.perf_counter()
        res = httpx.post("http://localhost:8000/api/v1/agentic/agentic-execute", json=payload, headers=headers, timeout=10.0)
        client_duration_ms = (time.perf_counter() - client_start) * 1000.0
        
        if res.status_code == 200:
            # Extract the custom latency calculation header injected by our backend profiler middleware
            backend_latency = res.headers.get("X-Process-Latency-MS", "N/A")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Client Round-Trip Time", f"{client_duration_ms:.1f} ms")
            with col2:
                st.metric("Internal Backend Execution", f"{backend_latency} ms")
            with col3:
                st.metric("Network Transport Overhead", f"{(client_duration_ms - float(backend_latency)):.1f} ms")
                
            st.success("Network connection layers are stable and optimized.")
            
            # Display detailed platform infrastructure specifications
            with st.expander("View Diagnostic Context Details"):
                st.json({
                    "Target URL": "http://localhost:8000/api/v1/agentic/agentic-execute",
                    "HTTP Status Protocol": res.status_code,
                    "Assigned Active Model Core": "llama-3.1-8b-instant",
                    "Orchestration Driver": "LangGraph Engine Stateful Core v2"
                })
        else:
            st.error(f"Diagnostic test failed with status code: {res.status_code}")
    except Exception as e:
        st.error(f"Network transport diagnostic crash: {str(e)}")