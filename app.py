import streamlit as st
import subprocess
import sys
import os
import json
import time
import threading
from datetime import datetime
import tempfile
import signal
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define agent type descriptions
AGENT_TYPES = {
    "Customer Support Specialist": "Resolves product issues, answers questions, and ensures satisfying customer experiences with technical knowledge and empathy.",
    "Lead Qualification Specialist": "Identifies qualified prospects, understands business challenges, and connects them with appropriate sales representatives.",
    "Appointment Scheduler": "Efficiently books, confirms, reschedules, or cancels appointments while providing clear service information.",
    "Info Collector": "Gathers accurate and complete information from customers while ensuring data quality and regulatory compliance.",
    "Care Coordinator": "Schedules medical appointments, answers health questions, and coordinates patient services with HIPAA compliance.",
    "Feedback Gatherer": "Conducts surveys, collects customer feedback, and gathers market research with high completion rates."
}

# Page config
st.set_page_config(
    page_title="AI Agent Caller Community",
    page_icon="📞",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .status-card {
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        background-color: #f8f9fa;
        margin: 1rem 0;
    }
    .agent-card {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        background-color: white;
    }
    .call-history-item {
        border-left: 3px solid #28a745;
        padding-left: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header"><h1>📞 AI Agent Caller - Community Edition</h1><p>Open Source VAPI Integration Platform</p></div>', unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    defaults = {
        "call_active": False,
        "call_history": [],
        "current_process": None,
        "show_descriptions": False,
        "last_error": None,
        "call_logs": [],
        "user_settings": {},
        "app_version": "1.0.0"
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# Create the isolated VAPI caller script
def create_vapi_caller_script():
    script_content = '''
import sys
import json
import time
import signal
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def signal_handler(signum, frame):
    logger.info("Call interrupted by user")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def main():
    try:
        # Import VAPI - handle potential import errors
        try:
            from vapi_python import Vapi
        except ImportError:
            logger.error("VAPI Python library not installed. Run: pip install vapi-python")
            sys.exit(1)
        
        # Read configuration from command line arguments
        if len(sys.argv) != 2:
            logger.error("Usage: python vapi_caller.py <config_json>")
            sys.exit(1)
       
        config = json.loads(sys.argv[1])
        api_key = config["api_key"]
        assistant_id = config["assistant_id"]
        overrides = config.get("overrides", {})
       
        logger.info(f"Initializing VAPI with assistant: {assistant_id}")
       
        # Initialize VAPI in isolated process
        vapi = Vapi(api_key=api_key)
       
        logger.info("Starting call...")
        call_response = vapi.start(
            assistant_id=assistant_id,
            assistant_overrides=overrides
        )
       
        call_id = getattr(call_response, 'id', 'unknown')
        logger.info(f"Call started successfully. Call ID: {call_id}")
       
        # Keep the process alive and monitor the call
        logger.info("Call is active. Press Ctrl+C to stop.")
       
        try:
            while True:
                time.sleep(1)
                # Optional: Add periodic status checks here
        except KeyboardInterrupt:
            logger.info("Stopping call...")
            try:
                vapi.stop()
                logger.info("Call stopped successfully")
            except Exception as e:
                logger.error(f"Error stopping call: {e}")
       
    except Exception as e:
        logger.error(f"Error in VAPI caller: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
   
    # Write script to temporary file
    script_path = os.path.join(tempfile.gettempdir(), "vapi_caller.py")
    with open(script_path, "w") as f:
        f.write(script_content)
   
    return script_path

# Function to start call in isolated process
def start_call_isolated(api_key, assistant_id, overrides=None):
    try:
        # Kill any existing process
        if st.session_state.current_process:
            try:
                st.session_state.current_process.terminate()
                st.session_state.current_process.wait(timeout=5)
            except:
                try:
                    st.session_state.current_process.kill()
                except:
                    pass
            st.session_state.current_process = None
       
        # Create the caller script
        script_path = create_vapi_caller_script()
       
        # Prepare configuration
        config = {
            "api_key": api_key,
            "assistant_id": assistant_id,
            "overrides": overrides or {}
        }
       
        config_json = json.dumps(config)
       
        # Start the isolated process
        process = subprocess.Popen(
            [sys.executable, script_path, config_json],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
       
        st.session_state.current_process = process
        st.session_state.call_active = True
        st.session_state.last_error = None
       
        # Add to call history
        st.session_state.call_history.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'assistant_id': assistant_id,
            'status': 'started',
            'process_id': process.pid
        })
       
        logger.info(f"Call started in isolated process (PID: {process.pid})")
        return True, f"Call started in isolated process (PID: {process.pid})"
       
    except Exception as e:
        error_msg = f"Failed to start isolated call: {str(e)}"
        st.session_state.last_error = error_msg
        st.session_state.call_active = False
        logger.error(error_msg)
        return False, error_msg

# Function to stop call
def stop_call_isolated():
    try:
        if st.session_state.current_process:
            # Send interrupt signal to gracefully stop the call
            st.session_state.current_process.terminate()
           
            # Wait for process to end
            try:
                st.session_state.current_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't respond
                st.session_state.current_process.kill()
                st.session_state.current_process.wait()
           
            st.session_state.current_process = None
       
        st.session_state.call_active = False
        st.session_state.last_error = None
       
        # Update call history
        if st.session_state.call_history:
            st.session_state.call_history[-1]['status'] = 'stopped'
       
        logger.info("Call stopped successfully")
        return True, "Call stopped successfully"
       
    except Exception as e:
        error_msg = f"Error stopping call: {str(e)}"
        st.session_state.last_error = error_msg
        # Force reset state
        st.session_state.call_active = False
        st.session_state.current_process = None
        logger.error(error_msg)
        return False, error_msg

# Function to check call status
def check_call_status():
    if st.session_state.current_process:
        poll_result = st.session_state.current_process.poll()
        if poll_result is not None:
            # Process has ended
            st.session_state.call_active = False
            st.session_state.current_process = None
           
            # Update call history
            if st.session_state.call_history:
                st.session_state.call_history[-1]['status'] = 'ended'
           
            return False, f"Call process ended with code: {poll_result}"
   
    return st.session_state.call_active, "Call is active"

# Sidebar
with st.sidebar:
    st.header("🔧 Configuration")
    
    # GitHub info
    st.markdown("### 🌟 Community Project")
    st.markdown("[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue)](https://github.com/yourusername/ai-agent-caller)")
    st.markdown("[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)")
    
    api_key = st.text_input("🔑 VAPI API Key", type="password", help="Enter your VAPI API key")
   
    # Status information
    st.subheader("📊 Status")
    call_active, status_msg = check_call_status()
    st.write(f"**Call Active:** {'✅ Yes' if call_active else '❌ No'}")
    st.write(f"**Total Calls:** {len(st.session_state.call_history)}")
    st.write(f"**Version:** {st.session_state.app_version}")
   
    if st.session_state.current_process:
        st.write(f"**Process ID:** {st.session_state.current_process.pid}")
   
    if st.session_state.last_error:
        st.error(f"**Last Error:** {st.session_state.last_error}")
   
    # Emergency controls
    st.subheader("🚨 Emergency Controls")
    if st.button("🔄 Reset All", help="Reset all session data"):
        if st.session_state.current_process:
            try:
                st.session_state.current_process.kill()
            except:
                pass
        st.session_state.clear()
        initialize_session_state()
        st.rerun()
   
    if st.button("💀 Force Kill Process", help="Force kill the current call process"):
        if st.session_state.current_process:
            try:
                st.session_state.current_process.kill()
                st.session_state.current_process = None
                st.session_state.call_active = False
                st.success("Process killed")
            except Exception as e:
                st.error(f"Error killing process: {e}")
   
    # Show descriptions toggle
    if st.button("ℹ️ Toggle Agent Types"):
        st.session_state.show_descriptions = not st.session_state.show_descriptions

# Show Agent Type Descriptions
if st.session_state.show_descriptions:
    st.subheader("📚 Agent Type Descriptions")
    for role, desc in AGENT_TYPES.items():
        with st.expander(role):
            st.write(desc)

# Main interface
if not api_key:
    st.warning("⚠️ Please enter your VAPI API key in the sidebar to get started.")
    st.markdown("""
    ### 🚀 Getting Started
    
    1. **Get your VAPI API Key** from [VAPI Dashboard](https://vapi.ai)
    2. **Enter your API key** in the sidebar
    3. **Configure your assistants** below
    4. **Start making calls!**
    
    ### 📖 Documentation
    
    - [VAPI Documentation](https://docs.vapi.ai)
    - [GitHub Repository](https://github.com/yourusername/ai-agent-caller)
    - [Community Discord](https://discord.gg/your-discord)
    """)
    st.stop()

# Agent Setup
st.subheader("🧠 Define Your Assistants")
agent_configs = []

# Create tabs for better organization
tab1, tab2, tab3, tab4 = st.tabs(["🤖 Assistant Setup", "📞 Call History", "📝 Live Logs", "ℹ️ About"])

with tab1:
    col1, col2 = st.columns(2)
   
    for i in range(1, 6):
        with col1 if i <= 2 else col2:
            with st.expander(f"Assistant {i} Setup", expanded=(i == 1)):
                agent_id = st.text_input(f"Assistant ID", key=f"assistant_id_{i}", help="Your VAPI assistant ID")
                agent_name = st.text_input(f"Agent Name", key=f"agent_name_{i}", placeholder="e.g., Customer Support Bot")
                agent_type = st.selectbox(
                    f"Agent Type",
                    options=[""] + list(AGENT_TYPES.keys()),
                    key=f"agent_type_{i}"
                )

                if agent_id and agent_type:
                    agent_configs.append({
                        "id": agent_id,
                        "name": agent_name or f"Agent {i}",
                        "type": agent_type
                    })

with tab2:
    st.subheader("📞 Call History")
    if st.session_state.call_history:
        for i, call in enumerate(reversed(st.session_state.call_history[-10:])):
            status_icon = {"started": "🟡", "stopped": "✅", "ended": "🔴"}.get(call['status'], "❓")
            with st.container():
                st.markdown(f'<div class="call-history-item">', unsafe_allow_html=True)
                st.write(f"{status_icon} **{call['timestamp']}** - {call['assistant_id']} ({call['status']})")
                if 'process_id' in call:
                    st.caption(f"Process ID: {call['process_id']}")
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("No calls made yet.")

with tab3:
    st.subheader("📝 Live Process Output")
    if st.session_state.current_process:
        if st.button("🔄 Refresh Logs"):
            pass  # Just refresh the page
       
        # Display logs
        if st.session_state.call_logs:
            for log in st.session_state.call_logs[-20:]:  # Show last 20 lines
                st.code(log, language=None)
        else:
            st.info("No logs available yet. Logs will appear here during calls.")
    else:
        st.info("No active call process.")

with tab4:
    st.subheader("ℹ️ About AI Agent Caller")
    st.markdown("""
    ### 🎯 Mission
    
    AI Agent Caller is an open-source community project designed to make VAPI integration simple and accessible for everyone.
    
    ### ✨ Features
    
    - **🛡️ Process Isolation**: Each call runs in its own protected process
    - **🔄 Zero Downtime**: Make unlimited calls without application restart
    - **📊 Live Monitoring**: Real-time process status and logging
    - **🚨 Emergency Controls**: Force kill and recovery options
    - **🤖 Multi-Agent**: Support for multiple AI assistants
    - **🌐 Community Driven**: Open source and collaborative
    
    ### 🤝 Contributing
    
    We welcome contributions! Check out our [GitHub repository](https://github.com/yourusername/ai-agent-caller) to:
    
    - 🐛 Report bugs
    - 💡 Suggest features
    - 🔧 Submit pull requests
    - 📖 Improve documentation
    
    ### 📞 Support
    
    - [GitHub Issues](https://github.com/yourusername/ai-agent-caller/issues)
    - [Community Discord](https://discord.gg/your-discord)
    - [Documentation](https://docs.your-app.com)
    """)

# User Info
st.subheader("🙋 Your Information")
col1, col2 = st.columns(2)
with col1:
    user_name = st.text_input("Your Name (for personalized greeting):", placeholder="Enter your name")
with col2:
    user_phone = st.text_input("Your Phone Number (optional):", placeholder="+1234567890")

# Select Agent to Call
if agent_configs:
    st.subheader("📲 Select Assistant")
    agent_labels = [f"{a['name']} - {a['type']}" for a in agent_configs]
    selected_index = st.selectbox(
        "Choose Assistant to Call",
        range(len(agent_configs)),
        format_func=lambda i: agent_labels[i]
    )
    selected_agent = agent_configs[selected_index]
   
    # Show selected agent details
    with st.expander("Selected Assistant Details", expanded=True):
        st.markdown(f'<div class="agent-card">', unsafe_allow_html=True)
        st.write(f"**Name:** {selected_agent['name']}")
        st.write(f"**Type:** {selected_agent['type']}")
        st.write(f"**ID:** {selected_agent['id']}")
        st.write(f"**Description:** {AGENT_TYPES[selected_agent['type']]}")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    selected_agent = None
    st.warning("⚠️ Please define at least one assistant above.")

# Call Controls
st.subheader("📞 Call Controls")

if selected_agent:
    col1, col2, col3 = st.columns(3)
   
    with col1:
        start_disabled = st.session_state.call_active
        if st.button("▶️ Start Call", disabled=start_disabled, use_container_width=True):
            overrides = {}
            if user_name:
                overrides["variableValues"] = {"name": user_name}
           
            # Clear previous logs
            st.session_state.call_logs = []
           
            success, message = start_call_isolated(api_key, selected_agent["id"], overrides)
            if success:
                st.success(f"📞 {message}")
                st.balloons()
                time.sleep(1)  # Brief pause before rerun
                st.rerun()
            else:
                st.error(f"❌ {message}")
   
    with col2:
        stop_disabled = not st.session_state.call_active
        if st.button("⛔ Stop Call", disabled=stop_disabled, use_container_width=True):
            success, message = stop_call_isolated()
            if success:
                st.success(f"📴 {message}")
                time.sleep(1)  # Brief pause before rerun
                st.rerun()
            else:
                st.error(f"❌ {message}")
   
    with col3:
        if st.button("🔄 Check Status", use_container_width=True):
            active, msg = check_call_status()
            if active:
                st.success(f"✅ {msg}")
            else:
                st.info(f"ℹ️ {msg}")

    # Call status indicator
    if st.session_state.call_active:
        st.markdown('<div class="status-card">', unsafe_allow_html=True)
        st.success("🟢 **Call is currently active in isolated process**")
        if st.session_state.current_process:
            st.info(f"Process ID: {st.session_state.current_process.pid}")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("🔴 **No active call**")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background-color: #f8f9fa; border-radius: 10px; margin: 2rem 0;">
    <h3>🚀 AI Agent Caller Community</h3>
    <p>Open Source • Community Driven • Always Free</p>
    <p>
        <a href="https://github.com/yourusername/ai-agent-caller" target="_blank">GitHub</a> • 
        <a href="https://discord.gg/your-discord" target="_blank">Discord</a> • 
        <a href="https://docs.your-app.com" target="_blank">Documentation</a>
    </p>
</div>
""", unsafe_allow_html=True)

# Auto-refresh for live updates
if st.session_state.call_active:
    time.sleep(2)
    st.rerun()
