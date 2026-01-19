import streamlit as st
import pandas as pd
import json
from src.tools.supabase_ops import SupabaseManager

def render_dashboard():
    st.header("Observability & Monitoring")
    
    try:
        manager = SupabaseManager()
        # Fetch logs
        # Note: In a real app we might want pagination, but for now fetch last 50
        response = manager.client.table("agent_logs").select("*").order("created_at", desc=True).limit(50).execute()
        logs = response.data
    except Exception as e:
        st.error(f"Failed to fetch logs: {e}")
        return

    if not logs:
        st.info("No logs found.")
        return

    # Metrics
    df = pd.DataFrame(logs)
    df['created_at'] = pd.to_datetime(df['created_at'])
    
    col1, col2, col3 = st.columns(3)
    
    total_runs = df[df['event_type'] == 'mission_start'].shape[0]
    success_runs = df[(df['event_type'] == 'mission_end') & (df['status'] == 'success')].shape[0]
    
    with col1:
        st.metric("Total Missions (Last 50 events)", total_runs)
    with col2:
        if total_runs > 0:
            rate = (success_runs / total_runs) * 100
            st.metric("Success Rate", f"{rate:.1f}%")
        else:
            st.metric("Success Rate", "N/A")
            
    # Activity Feed
    st.subheader("Activity Feed")
    
    for log in logs:
        with st.expander(f"{log['created_at']} - {log['agent_name']} - {log['event_type']} ({log['status']})"):
            st.write(f"**Message:** {log['message']}")
            if log.get('metadata'):
                st.json(log['metadata'])

if __name__ == "__main__":
    st.set_page_config(page_title="Observability Dashboard", layout="wide")
    render_dashboard()
