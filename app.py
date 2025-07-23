import streamlit as st
import streamlit.components.v1 as components

st.title("VAPI Widget Button Demo")

if st.button("Show VAPI Widget"):
    # Embed the widget HTML + script
    widget_html = """
    <vapi-widget assistant-id="a973c415-96a9-4c86-9422-877a7c6b81ed" 
                 public-key="be55f3ed-dde7-4cc1-8ac4-be6d1efd30bc"></vapi-widget>
    <script src="https://unpkg.com/@vapi-ai/client-sdk-react/dist/embed/widget.umd.js" async type="text/javascript"></script>
    """
    components.html(widget_html, height=600)
else:
    st.write("Click the button to load the assistant widget.")
