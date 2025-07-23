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
import sounddevice as sd
import numpy as np

# VAPI Python Features Configuration with SoundDevice
VAPI_API_KEY = "be55f3ed-dde7-4cc1-8ac4-be6d1efd30bc"

# Comprehensive Agent Configurations with Audio Features
VAPI_AGENTS = {
    "ad6c5243-9548-4231-9d04-b99c1628cc62": {
        "name": "Main Assistant",
        "type": "Customer Support",
        "voice": "jennifer",
        "language": "en-US",
        "features": ["transcription", "recording", "interruption_sensitivity", "audio_monitoring"]
    },
    "bf161516-6d88-490c-972e-274098a6b51a": {
        "name": "Agent CEO", 
        "type": "Executive Assistant",
        "voice": "mark",
        "language": "en-US",
        "features": ["sentiment_analysis", "call_summary", "lead_scoring", "audio_quality"]
    },
    "4fe7083e-2f28-4502-b6bf-4ae6ea71a8f4": {
        "name": "Agent Mindset",
        "type": "Life Coach",
        "voice": "sarah",
        "language": "en-US", 
        "features": ["emotion_detection", "conversation_flow", "personalization", "voice_analysis"]
    },
    "f8ef1ad5-5281-42f1-ae69-f94ff7acb453": {
        "name": "Agent Blogger",
        "type": "Content Creator",
        "voice": "alex",
        "language": "en-US",
        "features": ["content_generation", "topic_extraction", "keyword_analysis", "audio_recording"]
    },
    "7673e69d-170b-4319-bdf4-e74e5370e98a": {
        "name": "Agent Grant",
        "type": "Grant Writer",
        "voice": "michael",
        "language": "en-US",
        "features": ["document_analysis", "compliance_check", "funding_match", "voice_notes"]
    },
    "339cdad6-9989-4bb6-98ed-bd15521707d1": {
        "name": "Agent Prayer AI",
        "type": "Spiritual Guide",
        "voice": "grace",
        "language": "en-US",
        "features": ["empathy_mode", "cultural_sensitivity", "meditation_guide", "ambient_audio"]
    },
    "4820eab2-adaf-4f17-a8a0-30cab3e3f007": {
        "name": "Agent Metrics",
        "type": "Analytics Expert",
        "voice": "david",
        "language": "en-US",
        "features": ["data_visualization", "trend_analysis", "kpi_tracking", "audio_analytics"]
    },
    "f05c182f-d3d1-4a17-9c79-52442a9171b8": {
        "name": "Agent Researcher",
        "type": "Research Assistant",
        "voice": "emma",
        "language": "en-US",
        "features": ["fact_checking", "source_validation", "research_synthesis", "interview_recording"]
    },
    "1008771d-86ca-472a-a125-7a7e10100297": {
        "name": "Agent Investor",
        "type": "Investment Advisor",
        "voice": "robert",
        "language": "en-US",
        "features": ["market_analysis", "risk_assessment", "portfolio_optimization", "call_recording"]
    },
    "76f1d6e5-cab4-45b8-9aeb-d3e6f3c0c019": {
        "name": "Agent Newsroom",
        "type": "News Reporter",
        "voice": "jessica",
        "language": "en-US",
        "features": ["breaking_news", "fact_verification", "interview_mode", "broadcast_quality"]
    },
    "538258da-0dda-473d-8ef8-5427251f3ad5": {
        "name": "STREAMLIT Agent",
        "type": "Tech Support",
        "voice": "chris",
        "language": "en-US",
        "features": ["code_assistance", "debugging_help", "framework_guidance", "screen_recording"]
    },
    "14b94e2f-299b-4e75-a445-a4f5feacc522": {
        "name": "HTML/CSS Agent",
        "type": "Web Developer",
        "voice": "taylor",
        "language": "en-US",
        "features": ["code_review", "design_feedback", "accessibility_check", "demo_recording"]
    },
    "87d59105-723b-427e-a18d-da99fbf28608": {
        "name": "Business Plan Agent",
        "type": "Business Consultant",
        "voice": "patricia",
        "language": "en-US",
        "features": ["market_research", "financial_modeling", "strategy_planning", "presentation_audio"]
    },
    "04b80e02-9615-4c06-9424-93b4b1e2cdc9": {
        "name": "Ecom Agent",
        "type": "E-commerce Expert",
        "voice": "kevin",
        "language": "en-US",
        "features": ["product_recommendations", "sales_optimization", "customer_journey", "sales_calls"]
    },
    "7b2b8b86-5caa-4f28-8c6b-e7d3d0404f06": {
        "name": "Agent Health",
        "type": "Health Assistant",
        "voice": "maria",
        "language": "en-US",
        "features": ["symptom_analysis", "appointment_scheduling", "health_tracking", "consultation_recording"]
    },
    "232f3d9c-18b3-4963-bdd9-e7de3be156ae": {
        "name": "Cinch Closer",
        "type": "Sales Closer",
        "voice": "anthony",
        "language": "en-US",
        "features": ["objection_handling", "closing_techniques", "deal_scoring", "sales_recording"]
    },
    "41fe59e1-829f-4936-8ee5-eef2bb1287fe": {
        "name": "DISC Agent",
        "type": "Personality Assessor",
        "voice": "linda",
        "language": "en-US",
        "features": ["personality_analysis", "communication_style", "team_dynamics", "assessment_audio"]
    }
}

# Audio Configuration with SoundDevice
AUDIO_SETTINGS = {
    "sample_rate": 44100,
    "channels": 2,
    "dtype": np.float32,
    "blocksize": 1024,
    "device": None,  # Use default device
    "latency": "low"
}

# Page Configuration
st.set_page_config(
    page_title="VAPI SoundDevice Integration",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.audio-card {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    margin: 0.5rem 0;
}
.vapi-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    margin: 0.5rem 0;
}
.metric-card {
    background: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    border-left: 4px solid #007bff;
}
.status-active {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    padding: 0.5rem;
    border-radius: 5px;
}
.status-inactive {
    background: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
    padding: 0.5rem;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

# Title and Header
st.title("🎙️ VAPI + SoundDevice Integration")
st.markdown("### Advanced Audio Processing with VAPI Python Library")

# Initialize Session State
def initialize_session_state():
    defaults = {
        "call_active": False,
        "current_call_id": None,
        "call_history": [],
        "current_process": None,
        "selected_agent": None,
        "call_logs": [],
        "audio_recording": False,
        "audio_data": [],
        "audio_stream": None,
        "voice_settings": {
            "voice": "jennifer",
            "speed": 1.0,
            "pitch": 1.0,
            "volume": 0.8
        },
        "audio_settings": AUDIO_SETTINGS.copy(),
        "advanced_features": {
            "transcription": True,
            "sentiment_analysis": False,
            "interruption_sensitivity": 0.5,
            "background_noise_reduction": True,
            "audio_monitoring": True,
            "real_time_processing": False
        }
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# Audio Device Management with SoundDevice
def get_audio_devices():
    """Get available audio devices using sounddevice"""
    try:
        devices = sd.query_devices()
        input_devices = []
        output_devices = []
        
        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append((i, device['name']))
            if device['max_output_channels'] > 0:
                output_devices.append((i, device['name']))
        
        return input_devices, output_devices
    except Exception as e:
        st.error(f"Error querying audio devices: {e}")
        return [], []

def audio_callback(indata, frames, time, status):
    """Audio callback function for real-time processing"""
    if status:
        st.warning(f"Audio callback status: {status}")
    
    if st.session_state.audio_recording:
        # Store audio data for processing
        st.session_state.audio_data.append(indata.copy())
        
        # Real-time audio level monitoring
        volume_norm = np.linalg.norm(indata) * 10
        if hasattr(st.session_state, 'audio_level'):
            st.session_state.audio_level = volume_norm

def start_audio_monitoring():
    """Start audio monitoring with sounddevice"""
    try:
        if not st.session_state.audio_stream:
            st.session_state.audio_stream = sd.InputStream(
                callback=audio_callback,
                channels=st.session_state.audio_settings['channels'],
                samplerate=st.session_state.audio_settings['sample_rate'],
                blocksize=st.session_state.audio_settings['blocksize'],
                device=st.session_state.audio_settings['device'],
                dtype=st.session_state.audio_settings['dtype']
            )
            st.session_state.audio_stream.start()
            return True, "Audio monitoring started"
    except Exception as e:
        return False, f"Failed to start audio monitoring: {e}"

def stop_audio_monitoring():
    """Stop audio monitoring"""
    try:
        if st.session_state.audio_stream:
            st.session_state.audio_stream.stop()
            st.session_state.audio_stream.close()
            st.session_state.audio_stream = None
            return True, "Audio monitoring stopped"
    except Exception as e:
        return False, f"Failed to stop audio monitoring: {e}"

# Enhanced VAPI Caller Script with SoundDevice Integration
def create_vapi_sounddevice_script():
    script_content = '''import sys
import json
import time
from vapi_python import Vapi
import signal
import os
from datetime import datetime
import sounddevice as sd
import numpy as np

class VapiSoundDeviceCaller:
    def __init__(self, config):
        self.config = config
        self.vapi = Vapi(api_key=config["api_key"])
        self.call_id = None
        self.start_time = None
        self.audio_stream = None
        
    def setup_signal_handlers(self):
        def signal_handler(signum, frame):
            print(f"[{datetime.now()}] Call interrupted by user")
            self.cleanup()
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    def setup_audio_monitoring(self):
        """Setup audio monitoring with sounddevice"""
        try:
            def audio_callback(indata, frames, time, status):
                if status:
                    print(f"[{datetime.now()}] Audio status: {status}")
                
                # Calculate audio level
                volume_norm = np.linalg.norm(indata) * 10
                if volume_norm > 0.1:  # Only log significant audio
                    print(f"[{datetime.now()}] Audio level: {volume_norm:.2f}")
            
            audio_config = self.config.get("audio_settings", {})
            self.audio_stream = sd.InputStream(
                callback=audio_callback,
                channels=audio_config.get("channels", 2),
                samplerate=audio_config.get("sample_rate", 44100),
                blocksize=audio_config.get("blocksize", 1024),
                dtype=np.float32
            )
            
            self.audio_stream.start()
            print(f"[{datetime.now()}] Audio monitoring started")
            return True
            
        except Exception as e:
            print(f"[{datetime.now()}] Audio setup error: {e}")
            return False
    
    def start_call(self):
        try:
            print(f"[{datetime.now()}] Initializing VAPI with SoundDevice integration...")
            
            # Setup audio monitoring if enabled
            if self.config.get("advanced_features", {}).get("audio_monitoring", False):
                self.setup_audio_monitoring()
            
            # Enhanced call configuration
            call_config = {
                "assistant_id": self.config["assistant_id"],
                "assistant_overrides": self.config.get("overrides", {})
            }
            
            # Add voice settings
            if "voice_settings" in self.config:
                call_config["voice"] = self.config["voice_settings"]
            
            # Add advanced features
            if "advanced_features" in self.config:
                call_config["features"] = self.config["advanced_features"]
            
            print(f"[{datetime.now()}] Starting call with enhanced audio processing...")
            
            self.start_time = datetime.now()
            call_response = self.vapi.start(**call_config)
            
            self.call_id = getattr(call_response, 'id', f'call_{int(time.time())}')
            print(f"[{datetime.now()}] Call started successfully. Call ID: {self.call_id}")
            
            return True
            
        except Exception as e:
            print(f"[{datetime.now()}] Error starting call: {e}")
            return False
    
    def monitor_call(self):
        print(f"[{datetime.now()}] Enhanced call monitoring started with audio processing...")
        
        try:
            while True:
                # Enhanced monitoring with audio feedback
                elapsed = datetime.now() - self.start_time if self.start_time else None
                if elapsed:
                    print(f"[{datetime.now()}] Call duration: {elapsed}")
                
                # Audio quality monitoring
                if self.audio_stream and self.audio_stream.active:
                    print(f"[{datetime.now()}] Audio stream active - monitoring quality...")
                
                # VAPI call monitoring
                if hasattr(self, 'call_id') and self.call_id:
                    print(f"[{datetime.now()}] Monitoring VAPI call {self.call_id}...")
                
                time.sleep(5)  # Update every 5 seconds
                
        except KeyboardInterrupt:
            print(f"[{datetime.now()}] Monitoring interrupted")
            self.cleanup()
    
    def cleanup(self):
        """Cleanup audio and call resources"""
        try:
            # Stop audio monitoring
            if self.audio_stream:
                self.audio_stream.stop()
                self.audio_stream.close()
                print(f"[{datetime.now()}] Audio monitoring stopped")
            
            # Stop VAPI call
            if self.call_id:
                print(f"[{datetime.now()}] Stopping VAPI call {self.call_id}...")
                self.vapi.stop()
                
                if self.start_time:
                    duration = datetime.now() - self.start_time
                    print(f"[{datetime.now()}] Call completed. Duration: {duration}")
                
                print(f"[{datetime.now()}] Call stopped successfully")
            
        except Exception as e:
            print(f"[{datetime.now()}] Cleanup error: {e}")

def main():
    try:
        if len(sys.argv) != 2:
            print("Usage: python vapi_sounddevice_caller.py <config_json>")
            sys.exit(1)
        
        config = json.loads(sys.argv[1])
        caller = VapiSoundDeviceCaller(config)
        caller.setup_signal_handlers()
        
        if caller.start_call():
            caller.monitor_call()
        else:
            sys.exit(1)
            
    except Exception as e:
        print(f"[{datetime.now()}] Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()'''
    
    script_path = os.path.join(tempfile.gettempdir(), "vapi_sounddevice_caller.py")
    with open(script_path, "w") as f:
        f.write(script_content)
    
    return script_path

# Enhanced Call Management with SoundDevice
def start_enhanced_vapi_call(agent_id, voice_settings, advanced_features, audio_settings, user_overrides=None):
    try:
        if st.session_state.current_process:
            st.session_state.current_process.terminate()
            st.session_state.current_process = None
        
        script_path = create_vapi_sounddevice_script()
        
        config = {
            "api_key": VAPI_API_KEY,
            "assistant_id": agent_id,
            "voice_settings": voice_settings,
            "advanced_features": advanced_features,
            "audio_settings": audio_settings,
            "overrides": user_overrides or {}
        }
        
        config_json = json.dumps(config)
        
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
        st.session_state.current_call_id = f"call_{int(time.time())}"
        
        # Start local audio monitoring if enabled
        if advanced_features.get("audio_monitoring", False):
            start_audio_monitoring()
        
        # Add to call history
        st.session_state.call_history.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'agent_id': agent_id,
            'agent_name': VAPI_AGENTS[agent_id]['name'],
            'status': 'active',
            'process_id': process.pid,
            'features_used': list(advanced_features.keys()),
            'voice_settings': voice_settings,
            'audio_settings': audio_settings
        })
        
        return True, f"Enhanced VAPI call with SoundDevice started (PID: {process.pid})"
        
    except Exception as e:
        st.session_state.call_active = False
        return False, f"Failed to start call: {str(e)}"

def stop_enhanced_vapi_call():
    try:
        # Stop audio monitoring
        if st.session_state.audio_stream:
            stop_audio_monitoring()
        
        # Stop VAPI process
        if st.session_state.current_process:
            st.session_state.current_process.terminate()
            
            try:
                st.session_state.current_process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                st.session_state.current_process.kill()
                st.session_state.current_process.wait()
            
            st.session_state.current_process = None
        
        st.session_state.call_active = False
        st.session_state.current_call_id = None
        st.session_state.audio_recording = False
        
        # Update call history
        if st.session_state.call_history:
            st.session_state.call_history[-1]['status'] = 'completed'
        
        return True, "VAPI call and audio monitoring stopped successfully"
        
    except Exception as e:
        st.session_state.call_active = False
        st.session_state.current_process = None
        return False, f"Error stopping call: {str(e)}"

# Sidebar - Audio & VAPI Configuration
with st.sidebar:
    st.header("🎙️ Audio & VAPI Config")
    
    # API Key Display
    st.text_input("VAPI API Key", value=VAPI_API_KEY[:8] + "...", disabled=True, type="password")
    
    # Audio Device Selection
    st.subheader("🔊 Audio Devices")
    input_devices, output_devices = get_audio_devices()
    
    if input_devices:
        selected_input = st.selectbox(
            "Input Device",
            options=[dev[0] for dev in input_devices],
            format_func=lambda x: next(dev[1] for dev in input_devices if dev[0] == x),
            key="input_device"
        )
        st.session_state.audio_settings["device"] = selected_input
    
    # Call Status
    st.subheader("📊 Status")
    if st.session_state.call_active:
        st.markdown('<div class="status-active">🟢 VAPI Call Active</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-inactive">🔴 No Active Call</div>', unsafe_allow_html=True)
    
    if st.session_state.audio_stream:
        st.markdown('<div class="status-active">🎙️ Audio Monitoring Active</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-inactive">🎙️ Audio Monitoring Inactive</div>', unsafe_allow_html=True)
    
    st.write(f"📞 **Total Calls:** {len(st.session_state.call_history)}")
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    if st.button("🔄 Refresh Audio Devices", use_container_width=True):
        st.rerun()
    
    if st.button("🛑 Emergency Stop All", use_container_width=True):
        stop_enhanced_vapi_call()
        st.success("Emergency stop executed")
        st.rerun()

# Main Content Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🤖 Agent Selection", 
    "🎙️ Audio Settings", 
    "🔧 VAPI Features", 
    "📞 Call Management", 
    "📊 Live Monitoring",
    "📈 Analytics"
])

# Tab 1: Agent Selection
with tab1:
    st.subheader("🤖 Select VAPI Agent")
    
    # Agent selection
    agent_options = [(agent_id, f"{config['name']} - {config['type']}") 
                    for agent_id, config in VAPI_AGENTS.items()]
    
    selected_agent_id = st.selectbox(
        "Choose Agent",
        options=[opt[0] for opt in agent_options],
        format_func=lambda x: next(opt[1] for opt in agent_options if opt[0] == x),
        key="agent_selector"
    )
    
    st.session_state.selected_agent = selected_agent_id
    
    # Display agent details
    if selected_agent_id:
        agent_config = VAPI_AGENTS[selected_agent_id]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="vapi-card">
                <h4>🤖 {agent_config['name']}</h4>
                <p><strong>Type:</strong> {agent_config['type']}</p>
                <p><strong>Voice:</strong> {agent_config['voice']}</p>
                <p><strong>Language:</strong> {agent_config['language']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("**🚀 Audio-Enhanced Features:**")
            for feature in agent_config['features']:
                icon = "🎙️" if "audio" in feature else "🔧"
                st.write(f"{icon} {feature.replace('_', ' ').title()}")

# Tab 2: Audio Settings
with tab2:
    st.subheader("🎙️ SoundDevice Audio Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔊 Audio Parameters**")
        st.session_state.audio_settings["sample_rate"] = st.selectbox(
            "Sample Rate (Hz)",
            [22050, 44100, 48000, 96000],
            index=1
        )
        
        st.session_state.audio_settings["channels"] = st.selectbox(
            "Channels",
            [1, 2],
            index=1
        )
        
        st.session_state.audio_settings["blocksize"] = st.slider(
            "Block Size",
            min_value=256,
            max_value=4096,
            value=1024,
            step=256
        )
    
    with col2:
        st.markdown("**🎚️ Voice Settings**")
        st.session_state.voice_settings["voice"] = st.selectbox(
            "VAPI Voice",
            ["jennifer", "mark", "sarah", "alex", "michael", "grace", "david", "emma"],
            index=0
        )
        
        st.session_state.voice_settings["speed"] = st.slider(
            "Speech Rate",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1
        )
        
        st.session_state.voice_settings["volume"] = st.slider(
            "Volume Level",
            min_value=0.1,
            max_value=1.0,
            value=0.8,
            step=0.1
        )
    
    # Audio Test
    st.subheader("🎵 Audio Test")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎙️ Test Microphone", use_container_width=True):
            success, message = start_audio_monitoring()
            if success:
                st.success(message)
                st.session_state.audio_recording = True
            else:
                st.error(message)
    
    with col2:
        if st.button("⏹️ Stop Test", use_container_width=True):
            success, message = stop_audio_monitoring()
            if success:
                st.success(message)
                st.session_state.audio_recording = False
            else:
                st.error(message)
    
    with col3:
        if st.button("📊 Audio Info", use_container_width=True):
            try:
                st.info(f"Default device: {sd.default.device}")
                st.info(f"Sample rate: {sd.default.samplerate}")
            except Exception as e:
                st.error(f"Error getting audio info: {e}")

# Tab 3: VAPI Features
with tab3:
    st.subheader("🔧 Advanced VAPI Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 Real-time Features**")
        st.session_state.advanced_features["transcription"] = st.checkbox(
            "Live Transcription", value=True
        )
        st.session_state.advanced_features["sentiment_analysis"] = st.checkbox(
            "Sentiment Analysis", value=False
        )
        st.session_state.advanced_features["audio_monitoring"] = st.checkbox(
            "Audio Monitoring", value=True
        )
        st.session_state.advanced_features["real_time_processing"] = st.checkbox(
            "Real-time Audio Processing", value=False
        )
    
    with col2:
        st.markdown("**🎛️ Audio Control**")
        st.session_state.advanced_features["interruption_sensitivity"] = st.slider(
            "Interruption Sensitivity",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1
        )
        
        st.session_state.advanced_features["background_noise_reduction"] = st.checkbox(
            "Noise Reduction", value=True
        )

# Tab 4: Call Management
with tab4:
    st.subheader("📞 Enhanced Call Management")
    
    # User Information
    st.markdown("**👤 User Information**")
    col1, col2 = st.columns(2)
    
    with col1:
        user_name = st.text_input("Your Name", placeholder="Enter your name")
        user_phone = st.text_input("Phone Number", placeholder="+1234567890")
    
    with col2:
        user_email = st.text_input("Email", placeholder="your@email.com")
        user_company = st.text_input("Company", placeholder="Your Company")
    
    # Enhanced Call Controls
    st.markdown("**🎮 Enhanced Call Controls**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📞 Start VAPI + Audio", disabled=st.session_state.call_active, use_container_width=True):
            if st.session_state.selected_agent:
                user_overrides = {}
                if user_name:
                    user_overrides["variableValues"] = {
                        "name": user_name,
                        "phone": user_phone,
                        "email": user_email,
                        "company": user_company
                    }
                
                st.session_state.call_logs = []
                
                success, message = start_enhanced_vapi_call(
                    st.session_state.selected_agent,
                    st.session_state.voice_settings,
                    st.session_state.advanced_features,
                    st.session_state.audio_settings,
                    user_overrides
                )
                
                if success:
                    st.success(f"✅ {message}")
                    st.balloons()
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                st.warning("Please select an agent first")
    
    with col2:
        if st.button("⏹️ Stop All", disabled=not st.session_state.call_active, use_container_width=True):
            success, message = stop_enhanced_vapi_call()
            if success:
                st.success(f"✅ {message}")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ {message}")
    
    with col3:
        if st.button("🎙️ Audio Only", disabled=st.session_state.audio_stream is not None, use_container_width=True):
            success, message = start_audio_monitoring()
            if success:
                st.success(message)
            else:
                st.error(message)
    
    with col4:
        if st.button("📊 Status Check", use_container_width=True):
            st.info(f"VAPI: {'Active' if st.session_state.call_active else 'Inactive'}")
            st.info(f"Audio: {'Active' if st.session_state.audio_stream else 'Inactive'}")

# Tab 5: Live Monitoring
with tab5:
    st.subheader("📊 Live Audio & Call Monitoring")
    
    if st.session_state.call_active or st.session_state.audio_stream:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🎙️ Audio Status**")
            if hasattr(st.session_state, 'audio_level'):
                st.progress(min(st.session_state.audio_level / 10, 1.0))
                st.write(f"Audio Level: {st.session_state.audio_level:.2f}")
            else:
                st.write("No audio data available")
        
        with col2:
            st.markdown("**📞 Call Status**")
            if st.session_state.current_call_id:
                st.write(f"Call ID: {st.session_state.current_call_id}")
                st.write(f"Process: {st.session_state.current_process.pid if st.session_state.current_process else 'N/A'}")
            else:
                st.write("No active call")
        
        # Live Logs
        st.subheader("📝 Live Logs")
        if st.session_state.call_logs:
            for log in st.session_state.call_logs[-10:]:
                st.text(log)
        else:
            st.info("No logs available yet...")
    else:
        st.info("Start a call or audio monitoring to see live data")

# Tab 6: Analytics
with tab6:
    st.subheader("📈 Call & Audio Analytics")
    
    if st.session_state.call_history:
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <h4>📞 Total Calls</h4>
                <h2>{}</h2>
            </div>
            """.format(len(st.session_state.call_history)), unsafe_allow_html=True)
        
        with col2:
            active_calls = len([c for c in st.session_state.call_history if c['status'] == 'active'])
            st.markdown(f"""
            <div class="metric-card">
                <h4>🟢 Active</h4>
                <h2>{active_calls}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            completed_calls = len([c for c in st.session_state.call_history if c['status'] == 'completed'])
            st.markdown(f"""
            <div class="metric-card">
                <h4>✅ Completed</h4>
                <h2>{completed_calls}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            audio_enabled_calls = len([c for c in st.session_state.call_history 
                                     if c.get('audio_settings', {}).get('sample_rate')])
            st.markdown(f"""
            <div class="metric-card">
                <h4>🎙️ Audio Enhanced</h4>
                <h2>{audio_enabled_calls}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Call History
        st.subheader("📋 Enhanced Call History")
        for call in reversed(st.session_state.call_history[-5:]):
            with st.expander(f"📞 {call['timestamp']} - {call['agent_name']} ({call['status']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Agent:** {call['agent_name']}")
                    st.write(f"**Status:** {call['status']}")
                    st.write(f"**Process ID:** {call.get('process_id', 'N/A')}")
                
                with col2:
                    if 'audio_settings' in call:
                        st.write(f"**Sample Rate:** {call['audio_settings'].get('sample_rate', 'N/A')} Hz")
                        st.write(f"**Channels:** {call['audio_settings'].get('channels', 'N/A')}")
                    st.write(f"**Voice:** {call.get('voice_settings', {}).get('voice', 'N/A')}")
    else:
        st.info("📭 No call history available yet. Start your first enhanced call!")

# Auto-refresh for live updates
if st.session_state.call_active or st.session_state.audio_stream:
    time.sleep(2)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
### 🚀 VAPI + SoundDevice Integration Features:
- **🎙️ SoundDevice Audio Processing** - Professional audio handling without PyAudio issues
- **📞 Enhanced VAPI Calls** - Full VAPI Python library integration
- **🔊 Real-time Audio Monitoring** - Live audio level monitoring and processing
- **🎛️ Advanced Audio Controls** - Sample rate, channels, and device selection
- **📊 Live Analytics** - Real-time call and audio monitoring
- **🛡️ Process Isolation** - Stable call handling with audio integration
""")

# Dependencies Information
with st.expander("📦 Dependencies & Installation"):
    st.code("""
# Required packages (install with pip):
streamlit
sounddevice  # Replaces PyAudio - easier installation
numpy
vapi_python
subprocess
threading
tempfile
signal

# Installation command:
pip install streamlit sounddevice numpy vapi_python
""")
