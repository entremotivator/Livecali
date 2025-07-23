import streamlit as st
import subprocess
import sys
import os
import json
import time
from datetime import datetime
import tempfile
import signal

# Agent type descriptions
AGENT_TYPES = {
    "Customer Support Specialist": "Resolves product issues, answers questions, and ensures satisfying customer experiences with technical knowledge and empathy.",
    "Lead Qualification Specialist": "Identifies qualified prospects, understands business challenges, and connects them with appropriate sales representatives.",
    "Appointment Scheduler": "Efficiently books, confirms, reschedules, or cancels appointments while providing clear service information.",
    "Info Collector": "Gathers accurate and complete information from customers while ensuring data quality and regulatory compliance.",
    "Care Coordinator": "Schedules medical appointments, answers health questions, and coordinates patient services with HIPAA compliance.",
    "Feedback Gatherer": "Conducts surveys, collects customer feedback, and gathers market research with high completion rates."
}

st.set_page_config(page_title="AI Agent Caller - Streamlit Cloud", layout="wide")
st.title("📞 AI Agent Caller - Isolated Process")

# Initialize session state
def init_state():
    if "call_active" not in st.session_state:
        st.session_state.call_active = False
    if "call_history" not in st.session_state:
        st.session_state.call_history = []
    if "current_process" not in st.session_state:
        st.session_state.current_process = None
    if "show_descriptions" not in st.session_state:
        st.session_state.show_descriptions = False
    if "last_error" not in st.session_state:
        st.session_state.last_error = None
    if "call_logs" not in st.session_state:
        st.session_state.call_logs = []

init_state()

# Create the isolated VAPI caller script dynamically
def create_vapi_caller_script():
    script = '''
import sys
import json
import time
from vapi_python import Vapi
import signal

def signal_handler(signum, frame):
    print("Call interrupted")
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def main():
    if len(sys.argv) != 2:
        print("Usage: python vapi_caller.py <config_json>")
        sys.exit(1)
    config = json.loads(sys.argv[1])
    api_key = config["api_key"]
    assistant_id = config["assistant_id"]
    overrides = config.get("overrides", {})
    try:
        vapi = Vapi(api_key=api_key)
        print(f"Starting call for assistant {assistant_id}...")
        call_resp = vapi.start(assistant_id=assistant_id, assistant_overrides=overrides)
        call_id = getattr(call_resp, 'id', 'unknown')
        print(f"Call started, ID: {call_id}")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Call stopped by user")
        vapi.stop()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    path = os.path.join(tempfile.gettempdir(), "vapi_caller.py")
    with open(path, "w") as f:
        f.write(script)
    return path

def start_call(api_key, assistant_id, overrides=None):
    if st.session_state.current_process:
        try:
            st.session_state.current_process.terminate()
            st.session_state.current_process.wait(timeout=3)
        except:
            try:
                st.session_state.current_process.kill()
            except:
                pass
        st.session_state.current_process = None

    script_path = create_vapi_caller_script()
    config = {"api_key": api_key, "assistant_id": assistant_id, "overrides": overrides or {}}
    config_json = json.dumps(config)

    proc = subprocess.Popen(
        [sys.executable, script_path, config_json],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )
    st.session_state.current_process = proc
    st.session_state.call_active = True
    st.session_state.last_error = None
    st.session_state.call_history.append({
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "assistant_id": assistant_id,
        "status": "started",
        "pid": proc.pid
    })
    return proc.pid

def stop_call():
    proc = st.session_state.current_process
    if proc:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        st.session_state.current_process = None
    st.session_state.call_active = False
    if st.session_state.call_history:
        st.session_state.call_history[-1]["status"] = "stopped"

def get_process_logs():
    proc = st.session_state.current_process
    if proc:
        try:
            import select
            if hasattr(select, "select"):
                ready, _, _ = select.select([proc.stdout], [], [], 0)
                if ready:
                    line = proc.stdout.readline()
                    if line:
                        st.session_state.call_logs.append(f"{datetime.now().strftime('%H:%M:%S')} - {line.strip()}")
        except Exception:
            pass

# Sidebar
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("API Key", type="password")
    st.subheader("Status")
    st.write(f"Active Call: {'✅' if st.session_state.call_active else '❌'}")
    st.write(f"Total Calls Made: {len(st.session_state.call_history)}")
    if st.session_state.current_process:
        st.write(f"Process PID: {st.session_state.current_process.pid}")
    if st.session_state.last_error:
        st.error(f"Last Error: {st.session_state.last_error}")

    if st.button("Force Stop Call"):
        stop_call()
        st.experimental_rerun()

    if st.button("Reset App State"):
        if st.session_state.current_process:
            st.session_state.current_process.kill()
        st.session_state.clear()
        init_state()
        st.experimental_rerun()

    if st.button("Toggle Agent Descriptions"):
        st.session_state.show_descriptions = not st.session_state.show_descriptions

# Agent Descriptions
if st.session_state.show_descriptions:
    st.subheader("Agent Types")
    for name, desc in AGENT_TYPES.items():
        with st.expander(name):
            st.write(desc)

if not api_key:
    st.warning("Please enter your API Key in the sidebar to proceed.")
    st.stop()

# Assistant Setup
st.subheader("Define Assistants")
agent_configs = []

tabs = st.tabs(["Setup", "Call History", "Live Logs"])

with tabs[0]:
    cols = st.columns(2)
    for i in range(1, 6):
        with cols[i % 2]:
            with st.expander(f"Assistant {i}"):
                aid = st.text_input(f"Assistant ID", key=f"aid_{i}")
                aname = st.text_input(f"Assistant Name", key=f"aname_{i}")
                atype = st.selectbox("Agent Type", [""] + list(AGENT_TYPES.keys()), key=f"atype_{i}")
                if aid and atype:
                    agent_configs.append({"id": aid, "name": aname or f"Assistant {i}", "type": atype})

with tabs[1]:
    st.subheader("Call History")
    if st.session_state.call_history:
        for call in reversed(st.session_state.call_history[-10:]):
            icon = {"started": "🟡", "stopped": "✅", "ended": "🔴"}.get(call.get("status", ""), "❓")
            st.write(f"{icon} {call['timestamp']} - {call['assistant_id']} ({call['status']}) [PID: {call.get('pid', 'N/A')}]")
    else:
        st.info("No call history.")

with tabs[2]:
    st.subheader("Live Logs")
    if st.session_state.call_active:
        get_process_logs()
        for log in st.session_state.call_logs[-20:]:
            st.text(log)
        st.button("Refresh Logs")
    else:
        st.info("No active call to show logs.")

# User info
st.subheader("Your Info")
col1, col2 = st.columns(2)
with col1:
    user_name = st.text_input("Your Name", placeholder="Optional")
with col2:
    user_phone = st.text_input("Your Phone Number", placeholder="Optional")

# Select assistant to call
if agent_configs:
    st.subheader("Select Assistant to Call")
    labels = [f"{a['name']} ({a['type']})" for a in agent_configs]
    choice = st.selectbox("Choose Assistant", range(len(agent_configs)), format_func=lambda i: labels[i])
    selected_agent = agent_configs[choice]

    with st.expander("Assistant Details", expanded=True):
        st.write(f"Name: {selected_agent['name']}")
        st.write(f"Type: {selected_agent['type']}")
        st.write(f"ID: {selected_agent['id']}")
        st.write(f"Description: {AGENT_TYPES[selected_agent['type']]}")
else:
    selected_agent = None
    st.warning("Define at least one assistant.")

# Call controls
st.subheader("Call Controls")

if selected_agent:
    col1, col2, col3 = st.columns([1,1,1])

    with col1:
        disabled = st.session_state.call_active
        if st.button("▶️ Start Call", disabled=disabled):
            overrides = {}
            if user_name:
                overrides["variableValues"] = {"name": user_name}

            st.session_state.call_logs = []
            pid = start_call(api_key, selected_agent["id"], overrides)
            st.success(f"Call started with PID {pid}")
            st.balloons()
            time.sleep(1)
            st._rerun()

    with col2:
        disabled = not st.session_state.call_active
        if st.button("⏹ Stop Call", disabled=disabled):
            stop_call()
            st.success("Call stopped")
            time.sleep(1)
            st._rerun()

    with col3:
        if st.button("🔄 Check Status"):
            active, msg = False, "No active call"
            if st.session_state.current_process:
                ret = st.session_state.current_process.poll()
                if ret is None:
                    active = True
                    msg = "Call is running"
                else:
                    active = False
                    msg = f"Process ended with code {ret}"
            st.info(msg)

# Auto refresh live logs if call active
if st.session_state.call_active:
    time.sleep(2)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
#### Process Isolation Benefits
- Each call runs in its own process to prevent crashes affecting the main app.
- Clean state per call with no context bleeding.
- Emergency force kill available.
- Live monitoring with real-time logs.
- Supports multiple calls without restarting the app.
""")

