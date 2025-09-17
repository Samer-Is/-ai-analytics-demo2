"""
Multi-Domain AI Data Analytics Tool - Main Streamlit Application
Replicates the original MImic telecom tool interface and experience
Adapted for Banking, Hospital, and Marketing domains
"""

import streamlit as st
import os
import uuid
from datetime import datetime
from pathlib import Path
import json

from backend import LLMWorkflow, get_available_domains, validate_environment, DomainDataLoader

# Configure Streamlit page
st.set_page_config(
    page_title="AI Data Analytics Tool",
    page_icon="📊",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "current_domain" not in st.session_state:
    st.session_state.current_domain = None

if "workflow" not in st.session_state:
    st.session_state.workflow = None

if "domain_conversations" not in st.session_state:
    st.session_state.domain_conversations = {}

def clear_output_charts():
    """Clear all chart files from the output directory"""
    try:
        output_dir = Path("output")
        if output_dir.exists():
            for chart_file in output_dir.glob("*.png"):
                chart_file.unlink(missing_ok=True)
    except Exception as e:
        st.warning(f"Could not clear previous charts: {e}")

def initialize_workflow(domain: str) -> bool:
    """Initialize or switch workflow to specific domain"""
    try:
        # Save current conversation if switching domains
        if st.session_state.current_domain and st.session_state.current_domain != domain:
            st.session_state.domain_conversations[st.session_state.current_domain] = st.session_state.messages.copy()
        
        # Clean up previous workflow
        if st.session_state.workflow:
            st.session_state.workflow.cleanup()
        
        # Initialize new workflow
        workflow = LLMWorkflow()
        if workflow.initialize_domain(domain):
            st.session_state.workflow = workflow
            st.session_state.current_domain = domain
            
            # Restore conversation for this domain
            if domain in st.session_state.domain_conversations:
                st.session_state.messages = st.session_state.domain_conversations[domain].copy()
            else:
                st.session_state.messages = []
            
            return True
        else:
            st.error(f"Failed to initialize {domain} domain. Check Docker and data files.")
            return False
            
    except Exception as e:
        st.error(f"Error initializing workflow: {str(e)}")
        return False

def render_header():
    """Render main application header"""
    st.markdown(
        """
        # <center>🔍 <span style="color: #2E86AB;">AI</span> Data Analytics Tool v1.0</center>
        **<center>Enterprise-Grade Multi-Domain Business Intelligence</center>**
        """,
        unsafe_allow_html=True
    )

def render_sidebar():
    """Render sidebar with domain selection and information"""
    with st.sidebar:
        st.markdown(
            """
            # 🔍 AI Analytics

            
            <p style="font-size: 0.85em; color: grey; font-style: italic;">Built with enterprise-grade AI technology</p>
            """,
            unsafe_allow_html=True,
        )
        
        st.markdown("---")
        
        # Domain selection
        st.subheader("📂 Select Domain")
        available_domains = get_available_domains()
        
        if not available_domains:
            st.error("No domains available. Run data generation script first.")
            return
        
        # Domain selection dropdown
        domain_display_names = {
            'banking': '🏦 Banking',
            'hospital': '🏥 Hospital', 
            'education': '🎓 Education'
        }
        
        selected_domain = st.selectbox(
            "Choose analysis domain:",
            available_domains,
            format_func=lambda x: domain_display_names.get(x, x.title()),
            index=available_domains.index(st.session_state.current_domain) if st.session_state.current_domain in available_domains else 0
        )
        
        # Initialize domain if changed
        if selected_domain != st.session_state.current_domain:
            with st.spinner(f"Initializing {selected_domain} domain..."):
                if initialize_workflow(selected_domain):
                    # Clear previous charts when switching domains
                    clear_output_charts()
                    st.success(f"✅ {selected_domain.title()} domain ready!")
                    st.rerun()
        
        # Display domain information
        if st.session_state.current_domain:
            render_domain_info(st.session_state.current_domain)
        
        st.markdown("---")
        
        # New conversation button
        if st.button("➕ Start New Conversation", type="secondary"):
            if st.session_state.current_domain:
                st.session_state.domain_conversations[st.session_state.current_domain] = []
                st.session_state.messages = []
                st.session_state.session_id = str(uuid.uuid4())
                # Clear previous charts when starting new conversation
                clear_output_charts()
                st.rerun()
        
        # Clear charts button
        if st.button("🧹 Clear Charts", help="Remove all generated charts"):
            clear_output_charts()
            st.success("Charts cleared!")
            st.rerun()

def render_domain_info(domain: str):
    """Render information about the current domain"""
    try:
        loader = DomainDataLoader(domain)
        schema = loader.schema_data
        
        st.subheader(f"📊 {schema['domain_name']} Domain")
        # All domain information removed per user request
                
    except Exception as e:
        st.error(f"Error loading domain info: {str(e)}")

def render_messages():
    """Render chat message history"""
    for message in st.session_state.messages:
        if message["role"] == "user":
            with st.chat_message("user"):
                st.markdown(message["content"])
        elif message["role"] == "assistant":
            render_assistant_message(message)

def render_assistant_message(message):
    """Render assistant message with code and visualizations"""
    with st.chat_message("assistant"):
        # Main response
        if "content" in message:
            st.markdown(message["content"])
        
        # Generated code (collapsible)
        if "code" in message and message["code"]:
            with st.expander("🔧 View Generated Code", expanded=False):
                st.code(message["code"], language="python")
        
        # Output files (charts, downloads)
        if "output_files" in message:
            for file_info in message["output_files"]:
                file_path = file_info["file_path"]
                file_name = file_info["file_name"]
                
                if file_path.endswith(('.png', '.jpg', '.jpeg')):
                    if os.path.exists(file_path):
                        st.image(file_path, caption=file_name)
                else:
                    # Download button for other files
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            st.download_button(
                                label=f"📥 Download {file_name}",
                                data=f.read(),
                                file_name=file_name,
                                mime="application/octet-stream"
                            )

def process_user_input(user_input: str):
    """Process user input through the workflow"""
    if not st.session_state.workflow:
        st.error("Please select a domain first.")
        return
    
    # Add user message to history
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })
    
    # Process through workflow
    with st.spinner("Analyzing your request..."):
        try:
            # Pass conversation history to backend for context
            result = st.session_state.workflow.process_query(
                user_input, 
                st.session_state.session_id,
                conversation_history=st.session_state.messages
            )
            
            if result.get("success"):
                # Prepare assistant response
                assistant_message = {
                    "role": "assistant",
                    "content": result.get("final_answer", "Analysis completed."),
                    "domain": result.get("domain"),
                    "message_type": result.get("message_type")
                }
                
                # Add code and output files if available
                if "code_results" in result:
                    code_data = result["code_results"]
                    if "generated_code" in code_data:
                        assistant_message["code"] = code_data["generated_code"]
                    
                    execution_result = code_data.get("execution_result", {})
                    if execution_result.get("output_files"):
                        assistant_message["output_files"] = execution_result["output_files"]
                
                # Add to message history
                st.session_state.messages.append(assistant_message)
                
            else:
                error_msg = result.get("error", "Unknown error occurred")
                st.error(f"Analysis failed: {error_msg}")
                
                # Add error message to history
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": f"I encountered an error: {error_msg}. Please try rephrasing your question or contact support."
                })
                
        except Exception as e:
            st.error(f"Unexpected error: {str(e)}")
            st.session_state.messages.append({
                "role": "assistant",
                "content": "I encountered an unexpected error. Please try again or contact support."
            })

def main():
    """Main application logic"""
    # Environment validation
    env_checks = validate_environment()
    
    if not env_checks["openai_key"]:
        st.error("⚠️ **OpenAI API key not configured**")
        st.write("Please set your OpenAI API key in the `.env` file:")
        st.code("OPENAI_API_KEY=your_actual_api_key_here")
        st.stop()
    
    if not env_checks["python_available"]:
        st.error("⚠️ **Python environment issue**") 
        st.write("Please ensure Python is properly installed.")
        st.stop()
    
    if not env_checks["required_packages"]:
        st.error("⚠️ **Required packages missing**")
        st.write("Please install required packages:")
        st.code("pip install -r requirements.txt")
        st.stop()
    
    if not env_checks["data_directories"]:
        st.error("⚠️ **Data not generated**")
        st.write("Please generate the sample data:")
        st.code("python scripts/generate_simple_data.py")
        st.stop()
    
    if not env_checks["schemas_available"]:
        st.error("⚠️ **Domain schemas missing**")
        st.write("Please check the metadata directory contains domain schemas.")
        st.stop()
    
    # Show environment status
    with st.sidebar:
        st.success("🟢 Environment Ready")
        with st.expander("System Status", expanded=False):
            st.write("✅ OpenAI API Key configured")
            st.write("✅ Python environment ready")
            st.write("✅ Required packages installed")
            st.write("✅ Sample data generated")
            st.write("✅ Domain schemas loaded")
    
    # Render UI
    render_header()
    render_sidebar()
    render_messages()
    
    # Chat input
    if user_input := st.chat_input("Ask me anything about your data..."):
        with st.chat_message("user"):
            st.markdown(user_input)
        
        process_user_input(user_input)
        st.rerun()
    
    # Footer
    st.markdown(
        """
        ---
        <p style="font-size: 0.9em; color: grey; font-style: italic; text-align: center;">
        <b>AI Data Analytics Tool</b> can make mistakes. Please verify important information and data.
        </p>
        """,
        unsafe_allow_html=True,
    )

if __name__ == "__main__":
    main()
