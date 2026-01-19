
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure OpenRouter for CrewAI (if using OpenRouter)
if os.environ.get("OPENROUTER_API_KEY") and not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = os.environ.get("OPENROUTER_API_KEY")
    os.environ["OPENAI_API_BASE"] = "https://openrouter.ai/api/v1"
    # Default model if not specified
    if not os.environ.get("OPENAI_MODEL_NAME"):
        os.environ["OPENAI_MODEL_NAME"] = "openai/gpt-4o-mini" # Or any default model


from src.agents.orchestrator import OrchestratorAgent
from src.tools.supabase_ops import SupabaseManager


# Page Config
st.set_page_config(
    page_title="CrewAI News Manager",
    layout="wide",
    initial_sidebar_state="expanded"
)

from src.ui.callbacks import StreamlitCallbackHandler

# Sidebar
with st.sidebar:
    st.title("Settings")
    st.info("Configuration placeholders here (e.g., Model Selection)")
    st.divider()
    st.markdown("### Status")
    st.success("System: Online")

# Main Title and Navigation
st.title("CrewAI News Manager")

# Tab Navigation
tab_main, tab_dashboard = st.tabs(["Main Interface", "Observability Dashboard"])

# Main Interface Tab
with tab_main:

    # Layout
    col_chat, col_logs = st.columns([1, 1], gap="medium")

    # Initialize Chat History
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": "Hello! I am your AI News Assistant. How can I help you today?"})

    # Chat Column
    with col_chat:
        st.subheader("Chat")
        
        # Display History
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])
                
        # Input
        if prompt := st.chat_input("Enter instructions (e.g., 'Update the article about...')"):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
                

            with st.chat_message("assistant"):
                # Status visualization
                status_container = st.status("Thinking...", expanded=True)
                
                # Initialize Callback Handler targeting the Logs Column
                callback_handler = StreamlitCallbackHandler(col_logs)

                
                try:
                    orchestrator = OrchestratorAgent()
                    response = orchestrator.run_mission(prompt, callback_handler=callback_handler)
                    
                    status_container.update(label="Mission Complete!", state="complete", expanded=False)
                    st.write(str(response))
                    st.session_state.messages.append({"role": "assistant", "content": str(response)})
                except Exception as e:
                    status_container.update(label="Error", state="error")
                    st.error(f"An error occurred: {e}")


    from src.core.proposal import ProposalManager

    # Check for proposals
    proposal_manager = ProposalManager()
    pending_proposal = proposal_manager.get_proposal()

    with st.sidebar:
        st.title("Admin Controls")
        if pending_proposal:
            st.warning("⚠️ Pending Approval")
            st.json(pending_proposal)
            
            col_approve, col_reject = st.columns(2)
            if col_approve.button("Approve & Execute"):
                try:
                    manager = SupabaseManager()
                    proposal_type = pending_proposal.get("type", "update")
                    
                    if proposal_type == "update":
                        result = manager.update_record(
                            record_id=pending_proposal["id"],
                            data=pending_proposal["data"],
                            approval_given=True
                        )
                        st.success(f"Successfully updated record: {result}")
                    
                    elif proposal_type == "create":
                        result = manager.create_record(
                            data=pending_proposal["data"],
                            approval_given=True
                        )
                        st.success(f"Successfully created record: {result}")

                    proposal_manager.clear_proposal()
                    st.rerun() # Refresh to show updated state
                except Exception as e:
                    st.error(f"Operation failed: {e}")
                    
            if col_reject.button("Reject"):
                proposal_manager.clear_proposal()
                st.info("Proposal rejected.")
                st.rerun()
        else:
            st.info("No pending proposals.")

    # Logs Column
    with col_logs:
        st.subheader("Agent Logs")
        st.code("System initialized.\\nReady to process tasks...", language="bash")
        st.info("Execution logs will appear here during tasks.")

# Dashboard Tab
with tab_dashboard:
    from src.ui.dashboard import render_dashboard
    render_dashboard()
