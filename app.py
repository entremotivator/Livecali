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

# VAPI Python Features Configuration
VAPI_API_KEY = "be55f3ed-dde7-4cc1-8ac4-be6d1efd30bc"

# Comprehensive Agent Configurations with VAPI Features
VAPI_AGENTS = {
    "ad6c5243-9548-4231-9d04-b99c1628cc62": {
        "name": "Main Assistant",
        "type": "Customer Support",
        "voice": "jennifer",
        "language": "en-US",
        "features": ["transcription", "recording", "interruption_sensitivity"]
    },
    "bf161516-6d88-490c-972e-274098a6b51a": {
        "name": "Agent CEO", 
        "type": "Executive Assistant",
        "voice": "mark",
        "language": "en-US",
        "features": ["sentiment_analysis", "call_summary", "lead_scoring"]
    },
    "4fe7083e-2f28-4502-b6bf-4ae6ea71a8f4": {
        "name": "Agent Mindset",
        "type": "Life Coach",
        "voice": "sarah",
        "language": "en-US", 
        "features": ["emotion_detection", "conversation_flow", "personalization"]
    },
    "f8ef1ad5-5281-42f1-ae69-f94ff7acb453": {
        "name": "Agent Blogger",
        "type": "Content Creator",
        "voice": "alex",
        "language": "en-US",
        "features": ["content_generation", "topic_extraction", "keyword_analysis"]
    },
    "7673e69d-170b-4319-bdf4-e74e5370e98a": {
        "name": "Agent Grant",
        "type": "Grant Writer",
        "voice": "michael",
        "language": "en-US",
        "features": ["document_analysis", "compliance_check", "funding_match"]
    },
    "339cdad6-9989-4bb6-98ed-bd15521707d1": {
        "name": "Agent Prayer AI",
        "type": "Spiritual Guide",
        "voice": "grace",
        "language": "en-US",
        "features": ["empathy_mode", "cultural_sensitivity", "meditation_guide"]
    },
    "4820eab2-adaf-4f17-a8a0-30cab3e3f007": {
        "name": "Agent Metrics",
        "type": "Analytics Expert",
        "voice": "david",
        "language": "en-US",
        "features": ["data_visualization", "trend_analysis", "kpi_tracking"]
    },
    "f05c182f-d3d1-4a17-9c79-52442a9171b8": {
        "name": "Agent Researcher",
        "type": "Research Assistant",
        "voice": "emma",
        "language": "en-US",
        "features": ["fact_checking", "source_validation", "research_synthesis"]
    },
    "1008771d-86ca-472a-a125-7a7e10100297": {
        "name": "Agent Investor",
        "type": "Investment Advisor",
        "voice": "robert",
        "language": "en-US",
        "features": ["market_analysis", "risk_assessment", "portfolio_optimization"]
    },
    "76f1d6e5-cab4-45b8-9aeb-d3e6f3c0c019": {
        "name": "Agent Newsroom",
        "type": "News Reporter",
        "voice": "jessica",
        "language": "en-US",
        "features": ["breaking_news", "fact_verification", "interview_mode"]
    },
    "538258da-0dda-473d-8ef8-5427251f3ad5": {
        "name": "STREAMLIT Agent",
        "type": "Tech Support",
        "voice": "chris",
        "language": "en-US",
        "features": ["code_assistance", "debugging_help", "framework_guidance"]
    },
    "14b94e2f-299b-4e75-a445-a4f5feacc522": {
        "name": "HTML/CSS Agent",
        "type": "Web Developer",
        "voice": "taylor",
        "language": "en-US",
        "features": ["code_review", "design_feedback", "accessibility_check"]
    },
    "87d59105-723b-427e-a18d-da99fbf28608": {
        "name": "Business Plan Agent",
        "type": "Business Consultant",
        "voice": "patricia",
        "language": "en-US",
        "features": ["market_research", "financial_modeling", "strategy_planning"]
    },
    "04b80e02-9615-4c06-9424-93b4b1e2cdc9": {
        "name": "Ecom Agent",
        "type": "E-commerce Expert",
        "voice": "kevin",
        "language": "en-US",
        "features": ["product_recommendations", "sales_optimization", "customer_journey"]
    },
    "7b2b8b86-5caa-4f28-8c6b-e7d3d0404f06": {
        "name": "Agent Health",
        "type": "Health Assistant",
        "voice": "maria",
        "language": "en-US",
        "features": ["symptom_analysis", "appointment_scheduling", "health_tracking"]
    },
    "232f3d9c-18b3-4963-bdd9-e7de3be156ae": {
        "name": "Cinch Closer",
        "type": "Sales Closer",
        "voice": "anthony",
        "language": "en-US",
        "features": ["objection_handling", "closing_techniques", "deal_scoring"]
    },
    "41fe59e1-829f-4936-8ee5-eef2bb1287fe": {
        "name": "DISC Agent",
        "type": "Personality Assessor",
        "voice": "linda",
        "language": "en-US",
        "features": ["personality_analysis", "communication_style", "team_dynamics"]
    }
}

# VAPI Python Features
VAPI_FEATURES = {
    "Call Management": {
        "start": "Start voice calls with assistants",
        "stop": "Stop active calls",
        "pause": "Pause ongoing conversations",
        "resume": "Resume paused calls",
        "transfer": "Transfer calls between assistants"
    },
    "Voice Configuration": {
        "voice_selection": "Choose from multiple voice options",
        "speech_rate": "Adjust speaking speed",
        "pitch_control": "Modify voice pitch",
        "volume_control": "Set audio levels",
        "language_support": "Multi-language capabilities"
    },
    "Real-time Features": {
        "live_transcription": "Real-time speech-to-text",
        "sentiment_analysis": "Emotion detection during calls",
        "interruption_handling": "Smart conversation flow",
        "background_noise": "Noise cancellation",
        "echo_cancellation": "Audio quality enhancement"
    },
    "Analytics & Monitoring": {
        "call_analytics": "Detailed call metrics",
        "conversation_insights": "AI-powered analysis",
        "performance_tracking": "Assistant effectiveness",
        "usage_statistics": "API usage monitoring",
        "cost_tracking": "Call cost analysis"
    },
    "Integration Features": {
        "webhook_support": "Real-time event notifications",
        "custom_functions": "Execute custom code during calls",
        "crm_integration": "Connect with CRM systems",
        "calendar_sync": "Schedule and manage appointments",
        "database_queries": "Access external data sources"
    },
    "Advanced Capabilities": {
        "multi_turn_conversations": "Context-aware dialogues",
        "function_calling": "Execute specific actions",
        "knowledge_base": "Access custom information",
        "conversation_memory": "Remember previous interactions",
        "dynamic_responses": "Adaptive conversation flow"
    }
}

# Page Configuration
st.set_page_config(
    page_title="VAPI Python Features Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.feature-card {
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
.agent-card {
    background: #ffffff;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# Title and Header
st.title("🤖 VAPI Python Features Demo")
st.markdown("### Comprehensive Streamlit Interface for VAPI Python Library")

# Initialize Session State
def initialize_session_state():
    defaults = {
        "call_active": False,
        "current_call_id": None,
        "call_history": [],
        "current_process": None,
        "selected_agent": None,
        "call_logs": [],
        "call_analytics": {},
        "voice_settings": {
            "voice": "jennifer",
            "speed": 1.0,
            "pitch": 1.0,
            "volume": 0.8
        },
        "advanced_features": {
            "transcription": True,
            "sentiment_analysis": False,
            "interruption_sensitivity": 0.5,
            "background_noise_reduction": True
        }
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

initialize_session_state()

# Create VAPI Caller Script with Enhanced Features
def create_enhanced_vapi_script():
    script_content = '''import sys
import json
import time
from vapi_python import Vapi
import signal
import os
from datetime import datetime

class EnhancedVapiCaller:
    def __init__(self, config):
        self.config = config
        self.vapi = Vapi(api_key=config["api_key"])
        self.call_id = None
        self.start_time = None
        
    def setup_signal_handlers(self):
        def signal_handler(signum, frame):
            print(f"[{datetime.now()}] Call interrupted by user")
            self.stop_call()
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
    
    def start_call(self):
        try:
            print(f"[{datetime.now()}] Initializing VAPI with enhanced features...")
            
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
            
            print(f"[{datetime.now()}] Starting call with configuration: {json.dumps(call_config, indent=2)}")
            
            self.start_time = datetime.now()
            call_response = self.vapi.start(**call_config)
            
            self.call_id = getattr(call_response, 'id', f'call_{int(time.time())}')
            print(f"[{datetime.now()}] Call started successfully. Call ID: {self.call_id}")
            
            return True
            
        except Exception as e:
            print(f"[{datetime.now()}] Error starting call: {e}")
            return False
    
    def monitor_call(self):
        print(f"[{datetime.now()}] Call monitoring started. Press Ctrl+C to stop.")
        
        try:
            while True:
                # Simulate real-time monitoring
                elapsed = datetime.now() - self.start_time if self.start_time else None
                if elapsed:
                    print(f"[{datetime.now()}] Call duration: {elapsed}")
                
                # Add call analytics simulation
                if hasattr(self, 'call_id') and self.call_id:
                    print(f"[{datetime.now()}] Monitoring call {self.call_id}...")
                
                time.sleep(5)  # Update every 5 seconds
                
        except KeyboardInterrupt:
            print(f"[{datetime.now()}] Monitoring interrupted")
            self.stop_call()
    
    def stop_call(self):
        try:
            if self.call_id:
                print(f"[{datetime.now()}] Stopping call {self.call_id}...")
                self.vapi.stop()
                
                if self.start_time:
                    duration = datetime.now() - self.start_time
                    print(f"[{datetime.now()}] Call completed. Duration: {duration}")
                
                print(f"[{datetime.now()}] Call stopped successfully")
            else:
                print(f"[{datetime.now()}] No active call to stop")
                
        except Exception as e:
            print(f"[{datetime.now()}] Error stopping call: {e}")

def main():
    try:
        if len(sys.argv) != 2:
            print("Usage: python enhanced_vapi_caller.py <config_json>")
            sys.exit(1)
        
        config = json.loads(sys.argv[1])
        caller = EnhancedVapiCaller(config)
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
    
    script_path = os.path.join(tempfile.gettempdir(), "enhanced_vapi_caller.py")
    with open(script_path, "w") as f:
        f.write(script_content)
    
    return script_path

# Enhanced Call Management Functions
def start_enhanced_call(agent_id, voice_settings, advanced_features, user_overrides=None):
    try:
        if st.session_state.current_process:
            st.session_state.current_process.terminate()
            st.session_state.current_process = None
        
        script_path = create_enhanced_vapi_script()
        
        config = {
            "api_key": VAPI_API_KEY,
            "assistant_id": agent_id,
            "voice_settings": voice_settings,
            "advanced_features": advanced_features,
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
        
        # Add to call history
        st.session_state.call_history.append({
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'agent_id': agent_id,
            'agent_name': VAPI_AGENTS[agent_id]['name'],
            'status': 'active',
            'process_id': process.pid,
            'features_used': list(advanced_features.keys()),
            'voice_settings': voice_settings
        })
        
        return True, f"Enhanced call started (PID: {process.pid})"
        
    except Exception as e:
        st.session_state.call_active = False
        return False, f"Failed to start call: {str(e)}"

def stop_enhanced_call():
    try:
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
        
        # Update call history
        if st.session_state.call_history:
            st.session_state.call_history[-1]['status'] = 'completed'
        
        return True, "Call stopped successfully"
        
    except Exception as e:
        st.session_state.call_active = False
        st.session_state.current_process = None
        return False, f"Error stopping call: {str(e)}"

# Sidebar - VAPI Configuration
with st.sidebar:
    st.header("🔧 VAPI Configuration")
    
    # API Key Display
    st.text_input("API Key", value=VAPI_API_KEY[:8] + "...", disabled=True, type="password")
    
    # Call Status
    st.subheader("📊 Call Status")
    status_color = "🟢" if st.session_state.call_active else "🔴"
    st.write(f"{status_color} **Active:** {st.session_state.call_active}")
    st.write(f"📞 **Total Calls:** {len(st.session_state.call_history)}")
    
    if st.session_state.current_call_id:
        st.write(f"🆔 **Call ID:** {st.session_state.current_call_id}")
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    if st.button("🔄 Refresh Status", use_container_width=True):
        st.rerun()
    
    if st.button("🛑 Emergency Stop", use_container_width=True):
        if st.session_state.current_process:
            try:
                st.session_state.current_process.kill()
                st.session_state.call_active = False
                st.session_state.current_process = None
                st.success("Emergency stop executed")
            except Exception as e:
                st.error(f"Error: {e}")

# Main Content Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🤖 Agent Selection", 
    "🎙️ Voice Settings", 
    "⚡ Advanced Features", 
    "📞 Call Management", 
    "📊 Analytics & History"
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
            <div class="agent-card">
                <h4>🤖 {agent_config['name']}</h4>
                <p><strong>Type:</strong> {agent_config['type']}</p>
                <p><strong>Voice:</strong> {agent_config['voice']}</p>
                <p><strong>Language:</strong> {agent_config['language']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("**🚀 Available Features:**")
            for feature in agent_config['features']:
                st.write(f"• {feature.replace('_', ' ').title()}")
        
        st.code(f"Agent ID: {selected_agent_id}", language="text")

# Tab 2: Voice Settings
with tab2:
    st.subheader("🎙️ Voice Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.session_state.voice_settings["voice"] = st.selectbox(
            "Voice Selection",
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
    
    with col2:
        st.session_state.voice_settings["pitch"] = st.slider(
            "Voice Pitch",
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
    
    # Voice Settings Preview
    st.subheader("🔊 Current Voice Settings")
    st.json(st.session_state.voice_settings)

# Tab 3: Advanced Features
with tab3:
    st.subheader("⚡ Advanced VAPI Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🎯 Real-time Features**")
        st.session_state.advanced_features["transcription"] = st.checkbox(
            "Live Transcription", value=True
        )
        st.session_state.advanced_features["sentiment_analysis"] = st.checkbox(
            "Sentiment Analysis", value=False
        )
        st.session_state.advanced_features["background_noise_reduction"] = st.checkbox(
            "Noise Reduction", value=True
        )
    
    with col2:
        st.markdown("**🎛️ Conversation Control**")
        st.session_state.advanced_features["interruption_sensitivity"] = st.slider(
            "Interruption Sensitivity",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1
        )
        
        st.session_state.advanced_features["response_delay"] = st.slider(
            "Response Delay (ms)",
            min_value=0,
            max_value=2000,
            value=500,
            step=100
        )
    
    # Feature Categories
    st.subheader("📋 Available Feature Categories")
    
    for category, features in VAPI_FEATURES.items():
        with st.expander(f"🔧 {category}"):
            for feature, description in features.items():
                st.write(f"**{feature.replace('_', ' ').title()}:** {description}")

# Tab 4: Call Management
with tab4:
    st.subheader("📞 Call Management Center")
    
    # User Information
    st.markdown("**👤 User Information**")
    col1, col2 = st.columns(2)
    
    with col1:
        user_name = st.text_input("Your Name", placeholder="Enter your name")
        user_phone = st.text_input("Phone Number", placeholder="+1234567890")
    
    with col2:
        user_email = st.text_input("Email", placeholder="your@email.com")
        user_company = st.text_input("Company", placeholder="Your Company")
    
    # Call Controls
    st.markdown("**🎮 Call Controls**")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📞 Start Enhanced Call", disabled=st.session_state.call_active, use_container_width=True):
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
                
                success, message = start_enhanced_call(
                    st.session_state.selected_agent,
                    st.session_state.voice_settings,
                    st.session_state.advanced_features,
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
        if st.button("⏹️ Stop Call", disabled=not st.session_state.call_active, use_container_width=True):
            success, message = stop_enhanced_call()
            if success:
                st.success(f"✅ {message}")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"❌ {message}")
    
    with col3:
        if st.button("⏸️ Pause Call", disabled=not st.session_state.call_active, use_container_width=True):
            st.info("Pause functionality - Feature coming soon")
    
    with col4:
        if st.button("🔄 Resume Call", disabled=st.session_state.call_active, use_container_width=True):
            st.info("Resume functionality - Feature coming soon")
    
    # Current Call Status
    if st.session_state.call_active:
        st.success("🟢 **Call is currently active with enhanced features**")
        if st.session_state.current_process:
            st.info(f"Process ID: {st.session_state.current_process.pid}")
    else:
        st.info("⚫ **No active call**")

# Tab 5: Analytics & History
with tab5:
    st.subheader("📊 Call Analytics & History")
    
    # Call Statistics
    if st.session_state.call_history:
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
                <h4>🟢 Active Calls</h4>
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
            # Most used agent
            agent_usage = {}
            for call in st.session_state.call_history:
                agent_name = call.get('agent_name', 'Unknown')
                agent_usage[agent_name] = agent_usage.get(agent_name, 0) + 1
            
            most_used = max(agent_usage.items(), key=lambda x: x[1])[0] if agent_usage else "None"
            st.markdown(f"""
            <div class="metric-card">
                <h4>🏆 Top Agent</h4>
                <h3>{most_used}</h3>
            </div>
            """, unsafe_allow_html=True)
    
    # Call History Table
    st.subheader("📋 Recent Call History")
    
    if st.session_state.call_history:
        for i, call in enumerate(reversed(st.session_state.call_history[-10:])):
            status_icon = {"active": "🟢", "completed": "✅", "failed": "❌"}.get(call['status'], "❓")
            
            with st.expander(f"{status_icon} {call['timestamp']} - {call['agent_name']} ({call['status']})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Agent ID:** {call['agent_id']}")
                    st.write(f"**Process ID:** {call.get('process_id', 'N/A')}")
                    st.write(f"**Status:** {call['status']}")
                
                with col2:
                    st.write(f"**Features Used:** {', '.join(call.get('features_used', []))}")
                    if 'voice_settings' in call:
                        st.write(f"**Voice:** {call['voice_settings'].get('voice', 'N/A')}")
                        st.write(f"**Speed:** {call['voice_settings'].get('speed', 'N/A')}")
    else:
        st.info("📭 No call history available yet. Start your first call!")

# Live Updates
if st.session_state.call_active:
    time.sleep(3)
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
### 🚀 VAPI Python Features Demonstrated:
- **Enhanced Call Management** with real-time monitoring
- **Advanced Voice Configuration** with multiple settings
- **Real-time Features** including transcription and sentiment analysis
- **Process Isolation** for stable call handling
- **Comprehensive Analytics** and call history tracking
- **Multi-agent Support** with specialized capabilities
""")
