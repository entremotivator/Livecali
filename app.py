import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="AI Voice Assistant", layout="wide")
st.title("Click the Button to Talk with AI")

# Display the widget using HTML
components.html(
    """
    <vapi-widget
      public-key="be55f3ed-dde7-4cc1-8ac4-be6d1efd30bc"
      assistant-id="a973c415-96a9-4c86-9422-877a7c6b81ed"
      mode="voice"
      theme="dark"
      base-bg-color="#000000"
      accent-color="#14B8A6"
      cta-button-color="#000000"
      cta-button-text-color="#ffffff"
      border-radius="large"
      size="full"
      position="bottom-right"
      title="TALK WITH AI"
      start-button-text="Start"
      end-button-text="End Call"
      chat-first-message="Hey, How can I help you today?"
      chat-placeholder="Type your message..."
      voice-show-transcript="true"
      consent-required="true"
      consent-title="Terms and conditions"
      consent-content="By clicking 'Agree,' and each time I interact with this AI agent, I consent to the recording, storage, and sharing of my communications with third-party service providers, and as otherwise described in our Terms of Service."
      consent-storage-key="vapi_widget_consent"
    ></vapi-widget>

    <script src="https://unpkg.com/@vapi-ai/client-sdk-react/dist/embed/widget.umd.js" async type="text/javascript"></script>
    """,
    height=100,  # the widget loads as a floating bubble, no need for much height
)
