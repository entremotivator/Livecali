import streamlit as st
import requests
import json

st.set_page_config(page_title="🧠 AI Agent VAPI Caller", layout="centered")

# --- VAPI Call Function ---
def call_vapi(api_key, assistant_id, text):
    url = "https://api.vapi.ai/v1/synthesize"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "input": {"text": text},
        "voice": "en-US-JennyNeural",
        "options": {
            "speed": 1.0,
            "pitch": 1.0
        },
        "assistant_id": assistant_id
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return {"error": f"HTTP error: {e}\n{response.text}"}
    except Exception as e:
        return {"error": f"Unexpected error: {e}"}

# --- Streamlit UI ---
st.title("🤖 VAPI Agent Caller")
st.markdown("Call your AI assistant with custom text input.")

with st.form("vapi_form"):
    api_key = st.text_input("🔐 API Key", type="password")
    assistant_id = st.text_input("🧬 Assistant ID")
    user_input = st.text_area("🗣️ Message to AI", "Hello, how can I help you today?")
    submitted = st.form_submit_button("📞 Call Agent")

    if submitted:
        if not api_key or not assistant_id:
            st.warning("Please enter both API Key and Assistant ID.")
        else:
            with st.spinner("Contacting your agent..."):
                result = call_vapi(api_key, assistant_id, user_input)
            if "error" in result:
                st.error(result["error"])
            else:
                st.success("✅ Success!")
                st.json(result)
