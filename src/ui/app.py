
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
        
        # File Attachments Section
        st.divider()
        st.subheader("📎 File Attachments (Optional)")
        
        uploaded_files = st.file_uploader(
            "Upload images, PDFs, or CSV files (max 3 files, 10MB each)",
            type=['jpg', 'jpeg', 'png', 'webp', 'pdf', 'csv'],
            accept_multiple_files=True,
            help="Images will be used in articles. PDFs/CSVs will be analyzed for content.",
            key="file_uploader"
        )
        
        # Display uploaded files with validation
        if uploaded_files:
            # Limit to 3 files
            if len(uploaded_files) > 3:
                st.warning("⚠️ Maximum 3 files allowed. Only first 3 will be used.")
                uploaded_files = uploaded_files[:3]
            
            # Show file list
            st.caption("Uploaded files:")
            for file in uploaded_files:
                file_size_mb = file.size / (1024 * 1024)
                
                # Check size
                if file_size_mb > 10:
                    st.error(f"❌ {file.name} - Too large ({file_size_mb:.2f}MB). Max: 10MB")
                else:
                    st.success(f"✅ {file.name} ({file_size_mb:.2f}MB)")
        
        st.divider()
                
        # Input
        if prompt := st.chat_input("Enter instructions (e.g., 'Update the article about...'):"):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.write(prompt)
                

            with st.chat_message("assistant"):
                # Status visualization
                status_container = st.status("Thinking...", expanded=True)
                
                # Initialize Callback Handler targeting the Logs Column
                callback_handler = StreamlitCallbackHandler(col_logs)

                # Process attachments if any
                attachment_context = ""
                if uploaded_files:
                    with st.spinner("Processing attachments..."):
                        try:
                            from src.core.file_handler import process_files
                            
                            result = process_files(uploaded_files)
                            
                            # Add image URLs to context
                            if result['images']:
                                attachment_context += f"\n\nAttached Images:\n"
                                for idx, url in enumerate(result['images'], 1):
                                    attachment_context += f"{idx}. {url}\n"
                                st.info(f"✅ Uploaded {len(result['images'])} image(s)")
                            
                            # Add PDF content to context
                            if result['pdf_text']:
                                # Limit PDF text to avoid overwhelming the agent
                                pdf_preview = result['pdf_text'][:2000]
                                attachment_context += f"\n\nPDF Content (preview):\n{pdf_preview}...\n"
                                st.info(f"✅ Extracted text from PDF ({len(result['pdf_text'])} characters)")
                            
                            # Show errors if any
                            if result['errors']:
                                for error in result['errors']:
                                    st.warning(f"⚠️ {error}")
                        
                        except Exception as e:
                            st.error(f"❌ Error processing attachments: {e}")
                
                # Combine prompt with attachment context
                full_prompt = prompt + attachment_context
                
                try:
                    orchestrator = OrchestratorAgent()
                    response = orchestrator.run_mission(full_prompt, callback_handler=callback_handler)
                    
                    status_container.update(label="Mission Complete!", state="complete", expanded=False)
                    st.write(str(response))
                    st.session_state.messages.append({"role": "assistant", "content": str(response)})
                except Exception as e:
                    status_container.update(label="Error", state="error")
                    st.error(f"An error occurred: {e}")


    from src.core.proposal import ProposalManager

    # Check for proposals
    proposal_manager = ProposalManager()
    
    try:
        pending_proposals = proposal_manager.get_pending_proposals()
    except Exception as e:
        pending_proposals = []
        # Silently handle if table doesn't exist yet

    with st.sidebar:
        st.title("Admin Controls")
        
        if pending_proposals:
            st.warning(f"⚠️ {len(pending_proposals)} Pending Proposal(s)")
            
            for idx, proposal in enumerate(pending_proposals):
                with st.expander(f"Proposal {idx + 1}: {proposal['proposal_type'].upper()} - {proposal['created_at'][:19]}", expanded=True):
                    st.caption(f"ID: {proposal['id']}")
                    st.markdown(f"**Type:** {proposal['proposal_type']}")
                    st.markdown(f"**Reason:** {proposal.get('reason', 'N/A')}")
                    
                    # Show target record for updates
                    if proposal.get('target_record_id'):
                        st.markdown(f"**Target ID:** {proposal['target_record_id']}")
                    
                    # Show payload
                    st.markdown("**Payload:**")
                    st.json(proposal['payload'])
                    
                    # Action buttons
                    col_approve, col_reject = st.columns(2)
                    
                    # Approve button
                    if col_approve.button(f"✅ Approve", key=f"approve_{proposal['id']}"):
                        try:
                            proposal_manager.approve_proposal(proposal['id'])
                            st.success(f"Approved and executed!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Failed: {e}")
                    
                    # Reject button with feedback
                    if col_reject.button(f"❌ Reject", key=f"reject_{proposal['id']}"):
                        # Use a session state to track which proposal is being rejected
                        st.session_state[f"rejecting_{proposal['id']}"] = True
                        st.rerun()
                    
                    # Show feedback input if rejecting
                    if st.session_state.get(f"rejecting_{proposal['id']}", False):
                        feedback = st.text_area("Rejection reason (optional):", key=f"feedback_{proposal['id']}")
                        
                        col_submit, col_cancel = st.columns(2)
                        if col_submit.button("Submit Rejection", key=f"submit_reject_{proposal['id']}"):
                            try:
                                proposal_manager.reject_proposal(proposal['id'], feedback)
                                st.info("Proposal rejected.")
                                st.session_state[f"rejecting_{proposal['id']}"] = False
                                st.rerun()
                            except Exception as e:
                                st.error(f"Failed: {e}")
                        
                        if col_cancel.button("Cancel", key=f"cancel_reject_{proposal['id']}"):
                            st.session_state[f"rejecting_{proposal['id']}"] = False
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
