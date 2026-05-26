import streamlit as st
import httpx

st.set_page_config(page_title="Voice Portal", page_icon="🎙️", layout="wide")
st.subheader("🎙️ Hands-Free Clinical Voice Consultation Portal")
st.markdown("---")

if not st.session_state.get("user_token"):
    st.warning("⚠️ Access Denied. Please authenticate via the User Access portal to activate your voice interface.")
    st.stop()

headers = {"Authorization": f"Bearer {st.session_state['user_token']}"}

st.markdown("### 1. Audio Dictation Input")
st.write("Click below to record your symptoms or diagnostic notes directly from your microphone:")

# Initialize the native browser recording widget
audio_value = st.audio_input("Record your diagnostic inquiry")

if audio_value is not None:
    st.info("Audio input detected successfully.")
    
    if st.button("Transcribe & Process with LangGraph Core", type="primary"):
        # Package the audio recording data array as a multi-part form
        files = {"file": ("input_audio.wav", audio_value.getvalue(), "audio/wav")}
        
        with st.spinner("Groq Whisper executing transcription..."):
            try:
                # Step 1: Send the recording to our speech-to-text endpoint
                stt_res = httpx.post("http://localhost:8000/api/v1/medical/dictate-speech", files=files, headers=headers, timeout=30.0)
                
                if stt_res.status_code == 200:
                    user_prompt = stt_res.json()["transcription"]
                    st.success(f"**Transcribed Voice Text:** \"{user_prompt}\"")
                    
                    # Step 2: Route the transcribed text straight into our multi-agent orchestrator
                    st.markdown("---")
                    st.markdown("### 2. Agent Execution Strategy")
                    
                    with st.spinner("Processing text through LangGraph decision trees..."):
                        agent_payload = {"session_id": "voice-session-101", "message": user_prompt}
                        agent_res = httpx.post("http://localhost:8000/api/v1/agentic/agentic-execute", json=agent_payload, headers=headers, timeout=45.0)
                        
                        if agent_res.status_code == 200:
                            agent_data = agent_res.json()
                            ai_reply = agent_data["response"]
                            path_used = agent_data["dispatched_path"]
                            
                            st.caption(f"⚡ Dispatched Execution Route: `{path_used}`")
                            st.markdown(ai_reply)
                            
                            # Step 3: Send the response text back to the server to generate an audio readback file
                            with st.spinner("Synthesizing audio readback stream..."):
                                tts_payload = {"session_id": "voice", "message": ai_reply}
                                tts_res = httpx.post("http://localhost:8000/api/v1/medical/synthesize-speech", json=tts_payload, headers=headers, timeout=30.0)
                                
                                if tts_res.status_code == 200:
                                    st.markdown("---")
                                    st.markdown("### 3. Voice Playback Response")
                                    # Render a clean, native HTML5 audio playback player in the browser
                                    st.audio(tts_res.content, format="audio/mp3")
                                else:
                                    st.error("Speech synthesis pipeline timed out.")
                        else:
                            st.error("LangGraph orchestrator failed to return a valid response context.")
                else:
                    st.error(f"Transcription process interrupted. Code: {stt_res.status_code}")
                    
            except Exception as e:
                st.error(f"Audio pipeline network processing crash: {str(e)}")